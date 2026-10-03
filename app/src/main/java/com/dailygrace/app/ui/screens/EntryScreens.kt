package com.dailygrace.app.ui.screens

import android.Manifest
import android.os.Build
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.DailySchedule
import com.dailygrace.app.data.PrefsState
import com.dailygrace.app.notify.Reminder
import com.dailygrace.app.ui.EntryActions
import com.dailygrace.app.ui.components.EmptyState
import com.dailygrace.app.ui.components.GraceEntryPage
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.components.MenuAction
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Scripture
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

private val longDate = DateTimeFormatter.ofPattern("EEEE, MMMM d", Locale.getDefault())
private val fullDate = DateTimeFormatter.ofPattern("EEEE, MMMM d, yyyy", Locale.getDefault())
private val monthDay = DateTimeFormatter.ofPattern("MMMM d, yyyy", Locale.getDefault())

fun dayLabel(date: LocalDate, today: LocalDate = LocalDate.now()): String = when (date) {
    today -> "Today"
    today.minusDays(1) -> "Yesterday"
    else -> if (date.year == today.year) date.format(longDate) else date.format(fullDate)
}

/** Today's Grace: the home screen. */
@Composable
fun TodayScreen(
    content: Content,
    prefs: PrefsState,
    actions: EntryActions,
    bottomInset: Dp,
    onSettings: () -> Unit,
) {
    var today by remember { mutableStateOf(LocalDate.now()) }
    // The day can change while the app sits in the background.
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { today = LocalDate.now() }
    val entry = remember(today, content) { DailySchedule.entryFor(today, content.entries) }

    GraceEntryPage(
        entry = entry,
        eyebrow = "Today’s Grace",
        subtitle = today.format(longDate),
        isFavorite = entry.id in prefs.favorites,
        translationName = content.translation.name,
        onToggleFavorite = { actions.toggleFavorite(entry) },
        onSetWallpaper = { actions.setWallpaper(entry) },
        onShare = { actions.share(entry) },
        bottomInset = bottomInset,
        motion = prefs.gentleMotion,
        menu = listOf(MenuAction("Settings", onSettings)),
        extras = {
            if (!prefs.reminderEnabled && !prefs.reminderPromptDismissed) ReminderPrompt()
        },
    )
}

/** Any entry opened from Wallpapers, Favorites or History. */
@Composable
fun EntryDetailScreen(
    content: Content,
    id: String,
    date: String?,
    prefs: PrefsState,
    actions: EntryActions,
    bottomInset: Dp,
    onBack: () -> Unit,
) {
    val entry = content.entry(id)
    if (entry == null) {
        Box(Modifier.fillMaxSize().background(Grace.Night), contentAlignment = Alignment.Center) {
            EmptyState(GraceIcons.Wallpapers, "Not found", "This wallpaper is no longer in the app.") {
                OutlinedButton(onClick = onBack) { Text("Go back") }
            }
        }
        return
    }
    val day = date?.let { runCatching { LocalDate.parse(it) }.getOrNull() }
    GraceEntryPage(
        entry = entry,
        eyebrow = when {
            day == null -> entry.theme.ifBlank { "Daily Grace" }
            day == LocalDate.now() || day == LocalDate.now().minusDays(1) -> dayLabel(day)
            else -> day.dayOfWeek.getDisplayName(TextStyle.FULL, Locale.getDefault())
        },
        subtitle = day?.format(monthDay) ?: "",
        isFavorite = entry.id in prefs.favorites,
        translationName = content.translation.name,
        onToggleFavorite = { actions.toggleFavorite(entry) },
        onSetWallpaper = { actions.setWallpaper(entry) },
        onShare = { actions.share(entry) },
        bottomInset = bottomInset,
        motion = prefs.gentleMotion,
        onBack = onBack,
    )
}

/** Turns the daily reminder on or off, asking for notification permission on Android 13+. */
@Composable
fun rememberReminderToggle(): (Boolean) -> Unit {
    val context = LocalContext.current
    val app = context.applicationContext as DailyGraceApp
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        app.prefs.setReminder(granted)
        Reminder.sync(context)
        if (!granted) {
            Toast.makeText(context, "Notifications are off for Daily Grace. You can allow them in Android settings.", Toast.LENGTH_LONG).show()
        }
    }
    return remember(launcher) {
        { enable: Boolean ->
            if (enable && Build.VERSION.SDK_INT >= 33 && !Reminder.canPost(context)) {
                launcher.launch(Manifest.permission.POST_NOTIFICATIONS)
            } else {
                app.prefs.setReminder(enable)
                Reminder.sync(context)
            }
        }
    }
}

@Composable
private fun ColumnScope.ReminderPrompt() {
    val app = LocalContext.current.applicationContext as DailyGraceApp
    val toggle = rememberReminderToggle()
    val shape = RoundedCornerShape(24.dp)
    Spacer(Modifier.height(28.dp))
    Column(
        Modifier
            .padding(horizontal = 20.dp)
            .fillMaxWidth()
            .clip(shape)
            .background(Grace.Surface)
            .border(1.dp, Grace.Line, shape)
            .padding(20.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.Notifications, contentDescription = null, tint = Grace.Gold, modifier = Modifier.size(20.dp))
            Spacer(Modifier.width(10.dp))
            Text("A gentle morning reminder", style = MaterialTheme.typography.titleMedium, color = Grace.Ink)
        }
        Spacer(Modifier.height(8.dp))
        Text(
            "Receive Today’s Grace once a day at 7:00 AM. You can change the time or turn it off in Settings.",
            style = MaterialTheme.typography.bodyMedium,
            color = Grace.Muted,
        )
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = { toggle(true) },
                colors = ButtonDefaults.buttonColors(containerColor = Grace.Gold, contentColor = Grace.Night),
            ) { Text("Turn on") }
            TextButton(onClick = { app.prefs.dismissReminderPrompt() }) { Text("Not now", color = Grace.Muted) }
        }
    }
}

@Composable
fun LoadingScreen() {
    val fade = remember { Animatable(0f) }
    LaunchedEffect(Unit) { fade.animateTo(1f, tween(700)) }
    Box(Modifier.fillMaxSize().background(Grace.Night), contentAlignment = Alignment.Center) {
        Column(Modifier.alpha(fade.value), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(GraceIcons.Cross, contentDescription = null, tint = Grace.Gold, modifier = Modifier.size(36.dp))
            Spacer(Modifier.height(16.dp))
            Text("Daily Grace", fontFamily = Scripture, fontSize = 34.sp, color = Grace.Ink)
            Spacer(Modifier.height(6.dp))
            Text("A little reminder of God, every day.", style = MaterialTheme.typography.bodyMedium, color = Grace.Muted)
        }
    }
}

@Composable
fun LoadErrorScreen(message: String, onRetry: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Grace.Night), contentAlignment = Alignment.Center) {
        EmptyState(
            GraceIcons.Cross,
            "Something went wrong",
            "Daily Grace couldn’t open its verses. ($message)",
        ) {
            Button(onClick = onRetry, colors = ButtonDefaults.buttonColors(containerColor = Grace.Gold, contentColor = Grace.Night)) {
                Text("Try again", textAlign = TextAlign.Center)
            }
        }
    }
}
