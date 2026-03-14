package com.phantom.phantom_android

import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

object PhantomMethodChannel {
    private const val CHANNEL = "com.phantom/native"
    private var methodChannel: MethodChannel? = null
    private var context: Context? = null
    private val mainHandler = Handler(Looper.getMainLooper())

    fun register(flutterEngine: FlutterEngine, context: Context) {
        this.context = context
        methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        methodChannel?.setMethodCallHandler { call, result ->
            when (call.method) {
                "showOverlay" -> {
                    val contextJson = call.argument<String>("context")
                    val intent = Intent(context, PhantomFloatingService::class.java)
                    intent.putExtra("context", contextJson)
                    context.startService(intent)
                    result.success(true)
                }
                "injectText" -> {
                    val text = call.argument<String>("text")
                    if (text != null && PhantomAccessibilityService.instance != null) {
                        val success = PhantomAccessibilityService.instance!!.injectText(text)
                        result.success(success)
                    } else {
                        result.success(false)
                    }
                }
                "openAccessibilitySettings" -> {
                    val intent = Intent(android.provider.Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                    result.success(true)
                }
                else -> result.notImplemented()
            }
        }
    }

    fun sendContext(contextJson: String) {
        mainHandler.post {
            methodChannel?.invokeMethod("onContext", contextJson)
        }
    }
}