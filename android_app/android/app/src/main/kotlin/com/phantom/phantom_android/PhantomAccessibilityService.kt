package com.phantom.phantom_android

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import org.json.JSONObject

class PhantomAccessibilityService : AccessibilityService() {

    companion object {
        var instance: PhantomAccessibilityService? = null
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onUnbind(intent: android.content.Intent?): Boolean {
        if (instance == this) instance = null
        return super.onUnbind(intent)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        val eventType = event.eventType
        if (eventType == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED || eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            val rootNode = rootInActiveWindow ?: return
            
            val contextData = JSONObject()
            contextData.put("type", "accessibility_event")
            contextData.put("packageName", event.packageName?.toString() ?: "")
            
            val textNodes = mutableListOf<String>()
            findTextNodes(rootNode, textNodes)
            
            if (textNodes.isNotEmpty()) {
                contextData.put("textNodes", textNodes)
                PhantomMethodChannel.sendContext(contextData.toString())
            }
        }
    }
    
    private fun findTextNodes(node: AccessibilityNodeInfo, textNodes: MutableList<String>) {
        if (node.className == "android.widget.EditText" || node.className == "android.widget.TextView") {
            val text = node.text?.toString()
            if (!text.isNullOrBlank()) {
                textNodes.add(text)
            }
        }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                findTextNodes(child, textNodes)
                child.recycle()
            }
        }
    }

    fun injectText(text: String): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val focusNode = rootNode.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return false
        
        if (focusNode.isPassword) return false
        
        val arguments = Bundle()
        arguments.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        return focusNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
    }

    override fun onInterrupt() {
    }
}