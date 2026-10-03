package com.dailygrace.app

import android.app.Application
import com.dailygrace.app.data.ContentRepository
import com.dailygrace.app.data.UserPrefs
import com.dailygrace.app.image.AssetImages
import com.dailygrace.app.notify.Reminder

class DailyGraceApp : Application() {
    lateinit var content: ContentRepository
        private set
    lateinit var prefs: UserPrefs
        private set
    lateinit var images: AssetImages
        private set

    override fun onCreate() {
        super.onCreate()
        content = ContentRepository(this)
        prefs = UserPrefs(this)
        images = AssetImages(this)
        Reminder.createChannel(this)
        Reminder.sync(this)
    }
}
