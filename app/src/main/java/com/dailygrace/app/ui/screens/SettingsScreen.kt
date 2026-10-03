package com.dailygrace.app.ui.screens

import android.app.TimePickerDialog
import android.text.format.DateFormat
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dailygrace.app.BuildConfig
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.PrefsState
import com.dailygrace.app.notify.Reminder
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Scripture
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun SettingsScreen(content: Content, prefs: PrefsState, onBack: () -> Unit) {
    val context = LocalContext.current
    val app = context.applicationContext as DailyGraceApp
    val toggleReminder = rememberReminderToggle()
    val is24h = DateFormat.is24HourFormat(context)
    val time = LocalTime.of(prefs.reminderHour, prefs.reminderMinute)
    val timeText = time.format(DateTimeFormatter.ofPattern(if (is24h) "HH:mm" else "h:mm a", Locale.getDefault()))

    Column(
        Modifier
            .fillMaxSize()
            .background(Grace.Night)
            .verticalScroll(rememberScrollState())
            .statusBarsPadding()
            .navigationBarsPadding()
            .padding(bottom = 24.dp),
    ) {
        Row(Modifier.fillMaxWidth().height(60.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack, modifier = Modifier.padding(start = 4.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Grace.Ink)
            }
            Text("Settings", style = MaterialTheme.typography.titleLarge, color = Grace.Ink)
        }

        Group("Daily reminder") {
            SwitchRow(
                title = "Today’s Grace notification",
                body = "One quiet notification a day with the day’s verse.",
                checked = prefs.reminderEnabled,
                onChange = toggleReminder,
            )
            Divider()
            Row(
                Modifier
                    .fillMaxWidth()
                    .alpha(if (prefs.reminderEnabled) 1f else 0.45f)
                    .clickable(enabled = prefs.reminderEnabled) {
                        TimePickerDialog(context, { _, h, m ->
                            app.prefs.setReminderTime(h, m)
                            Reminder.sync(context)
                        }, prefs.reminderHour, prefs.reminderMinute, is24h).show()
                    }
                    .padding(horizontal = 20.dp, vertical = 18.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text("Time", style = MaterialTheme.typography.titleMedium, color = Grace.Ink)
                    Text("When the reminder arrives", style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
                }
                Text(timeText, style = MaterialTheme.typography.titleMedium, color = Grace.Gold)
            }
        }

        Group("Wallpaper") {
            SwitchRow(
                title = "Show the verse on wallpapers",
                body = "Turn off to set the artwork alone. You can also change this on each preview.",
                checked = prefs.wallpaperIncludesVerse,
                onChange = { app.prefs.setWallpaperIncludesVerse(it) },
            )
        }

        Group("Experience") {
            SwitchRow(
                title = "Gentle motion",
                body = "Let today’s artwork drift and breathe very slowly.",
                checked = prefs.gentleMotion,
                onChange = { app.prefs.setGentleMotion(it) },
            )
        }

        Group("About") {
            AboutRow("Scripture", "${content.translation.name} (${content.translation.code}). Public domain. One translation is used throughout.")
            Divider()
            AboutRow("Artwork", "Prototype artwork generated for Daily Grace. Final illustrations will replace it.")
            Divider()
            AboutRow("Privacy", "No account, no internet, no ads, no tracking. Your favorites stay on this phone.")
            Divider()
            AboutRow("Version", BuildConfig.VERSION_NAME)
        }

        Spacer(Modifier.height(28.dp))
        Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(GraceIcons.Cross, contentDescription = null, tint = Grace.Gold.copy(alpha = 0.7f))
            Spacer(Modifier.height(8.dp))
            Text("Daily Grace", fontFamily = Scripture, fontSize = 24.sp, color = Grace.Ink)
            Text("A little reminder of God, every day.", style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
        }
    }
}

@Composable
private fun Group(title: String, content: @Composable ColumnScope.() -> Unit) {
    val shape = RoundedCornerShape(22.dp)
    Text(
        title.uppercase(),
        style = MaterialTheme.typography.labelSmall,
        color = Grace.Gold,
        modifier = Modifier.padding(start = 28.dp, top = 24.dp, bottom = 10.dp),
    )
    Column(
        Modifier
            .padding(horizontal = 16.dp)
            .fillMaxWidth()
            .clip(shape)
            .background(Grace.Surface)
            .border(1.dp, Grace.Line, shape),
        content = content,
    )
}

@Composable
private fun Divider() = HorizontalDivider(Modifier.padding(horizontal = 20.dp), color = Grace.Line)

@Composable
private fun SwitchRow(title: String, body: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .clickable { onChange(!checked) }
            .padding(horizontal = 20.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleMedium, color = Grace.Ink)
            Spacer(Modifier.height(2.dp))
            Text(body, style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
        }
        Spacer(Modifier.width(16.dp))
        Switch(
            checked = checked,
            onCheckedChange = onChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Grace.Night,
                checkedTrackColor = Grace.Gold,
                uncheckedThumbColor = Grace.Muted,
                uncheckedTrackColor = Grace.SurfaceHigh,
                uncheckedBorderColor = Grace.Line,
            ),
        )
    }
}

@Composable
private fun AboutRow(title: String, body: String) {
    Box(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 16.dp)) {
        Column {
            Text(title, style = MaterialTheme.typography.titleSmall, color = Grace.Ink)
            Spacer(Modifier.height(2.dp))
            Text(body, style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
        }
    }
}
