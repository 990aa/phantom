use crate::AppContext;
use std::ffi::OsString;
use std::os::windows::ffi::OsStringExt;
use std::path::PathBuf;
use windows::core::{BSTR, Interface};
use windows::Win32::Foundation::{HWND, MAX_PATH, POINT};
use windows::Win32::System::Com::{CoInitializeEx, CoUninitialize, COINIT_MULTITHREADED};
use windows::Win32::System::ProcessStatus::GetProcessImageFileNameW;
use windows::Win32::System::Threading::{OpenProcess, PROCESS_QUERY_LIMITED_INFORMATION};
use windows::Win32::UI::Accessibility::{
    CUIAutomation, IUIAutomation, IUIAutomationTextPattern, UIA_TextPatternId,
};
use windows::Win32::UI::WindowsAndMessaging::{
    GetForegroundWindow, GetWindowTextW, GetWindowThreadProcessId,
};

fn get_window_title(hwnd: HWND) -> String {
    let mut buffer = [0u16; 512];
    let len = unsafe { GetWindowTextW(hwnd, &mut buffer) };
    OsString::from_wide(&buffer[..len as usize])
        .to_string_lossy()
        .into_owned()
}

fn get_process_name(hwnd: HWND) -> String {
    let mut pid = 0;
    unsafe { GetWindowThreadProcessId(hwnd, Some(&mut pid)) };
    if let Ok(process) = unsafe { OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid) } {
        let mut buffer = [0u16; MAX_PATH as usize];
        let len = unsafe { GetProcessImageFileNameW(process, &mut buffer) };
        if len > 0 {
            let full_path = OsString::from_wide(&buffer[..len as usize])
                .to_string_lossy()
                .into_owned();
            if let Some(name) = std::path::Path::new(&full_path).file_name() {
                return name.to_string_lossy().into_owned();
            }
        }
    }
    "unknown".to_string()
}

pub async fn grab_context() -> AppContext {
    let result = tokio::task::spawn_blocking(|| {
        unsafe { CoInitializeEx(None, COINIT_MULTITHREADED).ok() };
        let hwnd = unsafe { GetForegroundWindow() };
        let window_title = get_window_title(hwnd);
        let process_name = get_process_name(hwnd);
        
        let mut text_before = String::new();
        let mut text_after = String::new();
        let mut text_found = false;

        if let Ok(uia) = unsafe {
            windows::Win32::System::Com::CoCreateInstance::<_, IUIAutomation>(
                &CUIAutomation,
                None,
                windows::Win32::System::Com::CLSCTX_INPROC_SERVER,
            )
        } {
            if let Ok(element) = unsafe { uia.ElementFromHandle(hwnd) } {
                if let Ok(pattern) = unsafe { element.GetCurrentPatternAs::<IUIAutomationTextPattern>(UIA_TextPatternId) } {
                    if let Ok(selection) = unsafe { pattern.GetSelection() } {
                        if let Ok(_range) = unsafe { selection.GetElement(0) } {
                            if let Ok(doc_range) = unsafe { pattern.DocumentRange() } {
                                if let Ok(text) = unsafe { doc_range.GetText(-1) } {
                                    let txt = text.to_string();
                                    if !txt.is_empty() {
                                        text_before = txt;
                                        text_found = true;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        unsafe { CoUninitialize() };
        
        let mut screenshot_path = None;
        
        if !text_found {
            if let Ok(screens) = screenshots::Screen::all() {
                if let Some(screen) = screens.first() {
                    if let Ok(image) = screen.capture() {
                        let mut path = std::env::temp_dir();
                        path.push("phantom_ctx.png");
                        if image.save(&path).is_ok() {
                            screenshot_path = Some(path.to_string_lossy().into_owned());
                        }
                    }
                }
            }
        }

        AppContext {
            process_name,
            window_title,
            text_before,
            text_after,
            screenshot_path,
        }
    })
    .await
    .unwrap_or(AppContext {
        process_name: "unknown".into(),
        window_title: "unknown".into(),
        text_before: "".into(),
        text_after: "".into(),
        screenshot_path: None,
    });
    
    result
}
