#include <jni.h>
#include <string>
#include <thread>
#include <android/log.h>
#include "llama.cpp/include/llama.h"

#define TAG "PhantomLlama"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

#if defined(_WIN32)
#define FFI_PLUGIN_EXPORT __declspec(dllexport)
#else
#define FFI_PLUGIN_EXPORT __attribute__((visibility("default"))) __attribute__((used))
#endif

extern "C" {

struct LlamaContext {
    llama_model* model;
    llama_context* ctx;
};

typedef void (*NativeCallback)(const char* token);

FFI_PLUGIN_EXPORT int64_t phantom_load_model(const char* model_path) {
    LOGI("Loading model: %s", model_path);
    llama_backend_init();
    
    llama_model_params model_params = llama_model_default_params();
    llama_model* model = llama_load_model_from_file(model_path, model_params);
    if (!model) {
        LOGE("Failed to load model");
        return 0;
    }
    
    llama_context_params ctx_params = llama_context_default_params();
    ctx_params.n_ctx = 2048;
    llama_context* ctx = llama_new_context_with_model(model, ctx_params);
    if (!ctx) {
        LOGE("Failed to create context");
        llama_free_model(model);
        return 0;
    }
    
    LlamaContext* p_ctx = new LlamaContext{model, ctx};
    return reinterpret_cast<int64_t>(p_ctx);
}

FFI_PLUGIN_EXPORT void phantom_run_inference(int64_t ctx_handle, const char* prompt, NativeCallback callback) {
    LlamaContext* p_ctx = reinterpret_cast<LlamaContext*>(ctx_handle);
    if (!p_ctx || !p_ctx->model || !p_ctx->ctx) return;

    LOGI("Running inference for prompt: %s", prompt);
    // Simplified stub for Dart FFI integration
    std::string text = "This is a response from the Phantom Llama engine on Android.";
    std::string token = "";
    for (char c : text) {
        token += c;
        if (c == ' ' || c == '.') {
            callback(token.c_str());
            token = "";
            std::this_thread::sleep_for(std::chrono::milliseconds(50)); // simulate delay
        }
    }
    if (!token.empty()) callback(token.c_str());
    callback("[DONE]");
}

FFI_PLUGIN_EXPORT void phantom_run_vision_inference(int64_t ctx_handle, const char* image_path, const char* prompt, NativeCallback callback) {
    LOGI("Running vision inference for image: %s, prompt: %s", image_path, prompt);
    callback("This ");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    callback("is ");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    callback("a ");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    callback("caption.");
    callback("[DONE]");
}

FFI_PLUGIN_EXPORT void phantom_unload_model(int64_t ctx_handle) {
    LlamaContext* p_ctx = reinterpret_cast<LlamaContext*>(ctx_handle);
    if (p_ctx) {
        if (p_ctx->ctx) llama_free(p_ctx->ctx);
        if (p_ctx->model) llama_free_model(p_ctx->model);
        delete p_ctx;
    }
}

}