package com.dailygrace.app.ui.screens

import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.DailySchedule
import com.dailygrace.app.data.Prayer
import com.dailygrace.app.data.PrayerSection
import com.dailygrace.app.ui.components.Eyebrow
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Scripture
import java.time.LocalDate
import java.time.LocalTime

@Composable
fun PrayerScreen(content: Content, bottomInset: Dp) {
    val app = LocalContext.current.applicationContext as DailyGraceApp
    val sections by produceState<List<PrayerSection>?>(null) {
        value = runCatching { app.content.prayers() }.getOrDefault(emptyList())
    }
    val hour = remember { LocalTime.now().hour }
    val evening = hour >= 17 || hour < 4
    val today = remember { DailySchedule.entryFor(LocalDate.now(), content.entries) }
    val ordered = remember(sections, evening) {
        val list = sections.orEmpty()
        if (evening) list.sortedBy { if (it.id == "evening") 0 else 1 } else list
    }

    LazyColumn(
        Modifier.fillMaxSize().background(Grace.Night),
        contentPadding = PaddingValues(bottom = bottomInset + 20.dp),
    ) {
        item {
            ScreenHeader("Prayer", if (evening) "Good evening. Rest in His care." else "Good morning. Begin the day with God.")
        }
        today.prayer?.let { prayer ->
            item {
                TodayPrayerCard(prayer, today.reference)
            }
        }
        ordered.forEach { section ->
            item(key = "h_${section.id}") {
                Column(Modifier.padding(start = 24.dp, end = 24.dp, top = 28.dp, bottom = 10.dp)) {
                    Text(section.title, style = MaterialTheme.typography.titleLarge, color = Grace.Ink)
                    if (section.subtitle.isNotBlank()) {
                        Text(section.subtitle, style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
                    }
                }
            }
            items(section.prayers, key = { "p_${section.id}_${it.id}" }) { prayer ->
                PrayerCard(prayer, content.translation.code)
            }
        }
    }
}

@Composable
private fun TodayPrayerCard(prayer: String, reference: String) {
    val shape = RoundedCornerShape(26.dp)
    Column(
        Modifier
            .padding(horizontal = 16.dp)
            .fillMaxWidth()
            .clip(shape)
            .background(Brush.verticalGradient(listOf(Color(0xFF2A2433), Color(0xFF1B1E28))))
            .border(1.dp, Grace.Gold.copy(alpha = 0.25f), shape)
            .padding(24.dp),
    ) {
        Eyebrow("Today’s Prayer", GraceIcons.Prayer)
        Spacer(Modifier.height(14.dp))
        Text(prayer, fontFamily = Scripture, fontStyle = FontStyle.Italic, fontSize = 22.sp, lineHeight = 30.sp, color = Grace.Ink)
        Spacer(Modifier.height(14.dp))
        Text("Inspired by $reference", style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
    }
}

@Composable
private fun PrayerCard(prayer: Prayer, translationCode: String) {
    var open by rememberSaveable(prayer.id) { mutableStateOf(false) }
    val rotation by animateFloatAsState(if (open) 180f else 0f, label = "chevron")
    val shape = RoundedCornerShape(20.dp)
    Column(
        Modifier
            .padding(horizontal = 16.dp, vertical = 5.dp)
            .fillMaxWidth()
            .clip(shape)
            .background(Grace.Surface)
            .border(1.dp, Grace.Line, shape)
            .clickable { open = !open }
            .animateContentSize()
            .padding(horizontal = 20.dp, vertical = 18.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(prayer.title, style = MaterialTheme.typography.titleMedium, color = Grace.Ink)
                if (prayer.reference != null) {
                    Text("${prayer.reference} · $translationCode", style = MaterialTheme.typography.bodySmall, color = Grace.Gold.copy(alpha = 0.85f))
                }
            }
            Icon(
                GraceIcons.ChevronDown,
                contentDescription = if (open) "Collapse" else "Expand",
                tint = Grace.Muted,
                modifier = Modifier.size(20.dp).rotate(rotation),
            )
        }
        Spacer(Modifier.height(10.dp))
        if (open) {
            Text(
                prayer.text,
                fontFamily = if (prayer.scripture) Scripture else null,
                fontSize = if (prayer.scripture) 21.sp else 16.sp,
                lineHeight = if (prayer.scripture) 29.sp else 25.sp,
                color = Grace.Ink.copy(alpha = 0.92f),
            )
        } else {
            Text(
                prayer.text,
                style = MaterialTheme.typography.bodyMedium,
                color = Grace.Muted,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}
