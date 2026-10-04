package com.dailygrace.app.notify

import android.Manifest
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.MainActivity
import com.dailygrace.app.R
import com.dailygrace.app.data.DailySchedule
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneId

/**
 * One gentle notification per day at the user's chosen time. The alarm is allowed to fire while
 * the phone is idle (Doze); without that, phones that sit untouched overnight (Samsung especially)
 * hold the reminder back for hours or skip it. Exact timing is used when the system allows it.
 */
object Reminder {
    const val CHANNEL_ID = "todays_grace"
    private const val NOTIFICATION_ID = 1001
    private const val REQUEST_CODE = 7

    fun createChannel(context: Context) {
        val channel = NotificationChannel(
            CHANNEL_ID,
            context.getString(R.string.channel_name),
            NotificationManager.IMPORTANCE_DEFAULT,
        ).apply {
            description = context.getString(R.string.channel_description)
            setShowBadge(false)
        }
        context.getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    /** Schedules the next reminder if enabled, or cancels it. Safe to call any time. */
    fun sync(context: Context) {
        val prefs = (context.applicationContext as DailyGraceApp).prefs.state.value
        val am = context.getSystemService(AlarmManager::class.java)
        val pi = pendingIntent(context)
        am.cancel(pi)
        if (!prefs.reminderEnabled) return
        val trigger = nextTrigger(LocalDateTime.now(), prefs.reminderHour, prefs.reminderMinute)
        val millis = trigger.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        val exact = Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms()
        try {
            if (exact) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi)
            else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi)
        } catch (_: SecurityException) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi)
        }
    }

    /** False when notifications for the app (or its channel) are switched off in Android settings. */
    fun notificationsAllowed(context: Context): Boolean {
        if (!canPost(context)) return false
        val nm = NotificationManagerCompat.from(context)
        if (!nm.areNotificationsEnabled()) return false
        val channel = context.getSystemService(NotificationManager::class.java).getNotificationChannel(CHANNEL_ID)
        return channel == null || channel.importance != NotificationManager.IMPORTANCE_NONE
    }

    fun nextTrigger(now: LocalDateTime, hour: Int, minute: Int): LocalDateTime {
        val todayAt = LocalDateTime.of(now.toLocalDate(), LocalTime.of(hour, minute))
        return if (todayAt.isAfter(now.plusSeconds(30))) todayAt else todayAt.plusDays(1)
    }

    fun canPost(context: Context): Boolean =
        Build.VERSION.SDK_INT < 33 ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    fun show(context: Context) {
        if (!canPost(context)) return
        val app = context.applicationContext as DailyGraceApp
        val content = runCatching { app.content.contentBlocking() }.getOrNull() ?: return
        val entry = DailySchedule.entryFor(LocalDate.now(), content.entries)
        val open = PendingIntent.getActivity(
            context, 0,
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        val verse = "“${entry.verse}”"
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Today’s Grace")
            .setContentText(verse)
            .setStyle(NotificationCompat.BigTextStyle().bigText("$verse\n${entry.reference}\n\nOpen Today’s Grace →"))
            .setSubText(entry.reference)
            .setColor(0xFFE2C188.toInt())
            .setContentIntent(open)
            .setAutoCancel(true)
            .setOnlyAlertOnce(true)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        try {
            NotificationManagerCompat.from(context).notify(NOTIFICATION_ID, notification)
        } catch (_: SecurityException) {
            // Permission revoked between the check and the post; nothing to do.
        }
    }

    private fun pendingIntent(context: Context): PendingIntent = PendingIntent.getBroadcast(
        context, REQUEST_CODE,
        Intent(context, ReminderReceiver::class.java),
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
    )
}

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Reminder.show(context)
        Reminder.sync(context)
    }
}

/** Alarms are cleared on reboot, update and clock changes; put tomorrow's reminder back. */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Reminder.sync(context)
    }
}
