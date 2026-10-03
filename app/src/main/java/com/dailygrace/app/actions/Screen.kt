package com.dailygrace.app.actions

import android.content.Context
import android.os.Build
import android.util.DisplayMetrics
import android.view.WindowManager
import kotlin.math.max
import kotlin.math.min

/** The phone's full physical screen in portrait pixels (including system bar areas). */
fun physicalScreenSize(context: Context): Pair<Int, Int> {
    val wm = context.getSystemService(WindowManager::class.java)
    val (w, h) = if (Build.VERSION.SDK_INT >= 30) {
        val b = wm.maximumWindowMetrics.bounds
        b.width() to b.height()
    } else {
        val dm = DisplayMetrics()
        @Suppress("DEPRECATION")
        wm.defaultDisplay.getRealMetrics(dm)
        dm.widthPixels to dm.heightPixels
    }
    return min(w, h) to max(w, h)
}
