use serde_json::json;

// Simplified tests since we can't fully test COM or global hotkeys in CI without a desktop session.

#[test]
fn test_ipc_serialization() {
    let ctx = phantom_watcher::AppContext {
        process_name: "test.exe".into(),
        window_title: "Test Window".into(),
        text_before: "hello ".into(),
        text_after: " world".into(),
        screenshot_path: None,
    };
    
    let serialized = serde_json::to_string(&ctx).unwrap();
    assert!(serialized.contains("test.exe"));
    
    let deserialized: phantom_watcher::AppContext = serde_json::from_str(&serialized).unwrap();
    assert_eq!(deserialized.process_name, "test.exe");
}
