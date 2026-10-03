package com.dailygrace.app.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.DailySchedule
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.data.PrefsState
import com.dailygrace.app.image.rememberAssetImage
import com.dailygrace.app.ui.EntryActions
import com.dailygrace.app.ui.components.EmptyState
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Scripture
import java.time.LocalDate

/** Large serif title used at the top of the browsing screens. */
@Composable
fun ScreenHeader(title: String, subtitle: String? = null, modifier: Modifier = Modifier, horizontal: Dp = 24.dp) {
    Column(modifier.fillMaxWidth().statusBarsPadding().padding(start = horizontal, end = horizontal, top = 20.dp, bottom = 12.dp)) {
        Text(title, style = MaterialTheme.typography.headlineMedium, color = Grace.Ink)
        if (subtitle != null) {
            Spacer(Modifier.height(4.dp))
            Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = Grace.Muted)
        }
    }
}

/** A 20:9 thumbnail with the reference set quietly at the bottom. */
@Composable
fun WallpaperThumb(
    entry: GraceEntry,
    isFavorite: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(20.dp)
    val image by rememberAssetImage(entry.thumbPath, 432)
    val alpha by animateFloatAsState(if (image != null) 1f else 0f, tween(300), label = "thumb")
    Box(
        modifier
            .aspectRatio(9f / 20f)
            .clip(shape)
            .background(Grace.SurfaceHigh)
            .border(1.dp, Color.White.copy(alpha = 0.06f), shape)
            .clickable(onClickLabel = entry.reference, onClick = onClick),
    ) {
        image?.let {
            Image(it, contentDescription = null, modifier = Modifier.fillMaxSize().alpha(alpha), contentScale = ContentScale.Crop)
        }
        Box(
            Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .height(110.dp)
                .background(Brush.verticalGradient(listOf(Color.Transparent, Color.Black.copy(alpha = 0.7f))))
        )
        Column(Modifier.align(Alignment.BottomStart).padding(14.dp)) {
            Text(entry.reference, style = MaterialTheme.typography.titleSmall, color = Color.White, maxLines = 1, overflow = TextOverflow.Ellipsis)
            if (entry.theme.isNotBlank()) {
                Text(entry.theme, style = MaterialTheme.typography.bodySmall, color = Grace.GoldSoft.copy(alpha = 0.9f), maxLines = 1)
            }
        }
        if (isFavorite) {
            Icon(
                Icons.Filled.Favorite,
                contentDescription = "Saved",
                tint = Grace.Gold,
                modifier = Modifier.align(Alignment.TopEnd).padding(12.dp).size(18.dp),
            )
        }
    }
}

@Composable
private fun CategoryChip(label: String, selected: Boolean, onClick: () -> Unit) {
    val shape = RoundedCornerShape(50)
    Text(
        label,
        style = MaterialTheme.typography.labelLarge,
        color = if (selected) Grace.Night else Grace.Ink.copy(alpha = 0.85f),
        modifier = Modifier
            .clip(shape)
            .background(if (selected) Grace.Gold else Grace.Surface)
            .border(1.dp, if (selected) Grace.Gold else Grace.Line, shape)
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 9.dp),
    )
}

/** Wallpaper browser with category filter. */
@Composable
fun WallpapersScreen(content: Content, actions: EntryActions, bottomInset: Dp, prefs: PrefsState? = null) {
    var category by rememberSaveable { mutableStateOf<String?>(null) }
    val categories = remember(content) { content.categories.filter { c -> content.entries.any { c in it.categories } } }
    val shown = remember(category, content) { category?.let { content.inCategory(it) } ?: content.entries }

    LazyVerticalGrid(
        columns = GridCells.Adaptive(150.dp),
        modifier = Modifier.fillMaxSize().background(Grace.Night),
        contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = bottomInset + 16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item(span = { GridItemSpan(maxLineSpan) }) {
            ScreenHeader("Wallpapers", "${content.entries.size} verses · ${content.translation.name}", horizontal = 8.dp)
        }
        item(span = { GridItemSpan(maxLineSpan) }) {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                contentPadding = PaddingValues(vertical = 4.dp),
                modifier = Modifier.padding(bottom = 8.dp),
            ) {
                item { CategoryChip("All", category == null) { category = null } }
                items(categories) { c -> CategoryChip(c, category == c) { category = if (category == c) null else c } }
            }
        }
        items(shown, key = { it.id }) { entry ->
            WallpaperThumb(entry, isFavorite = prefs?.favorites?.contains(entry.id) == true) { actions.open(entry, null) }
        }
    }
}

@Composable
fun FavoritesScreen(content: Content, prefs: PrefsState, actions: EntryActions, bottomInset: Dp, onBrowse: () -> Unit) {
    val saved = remember(prefs.favoriteOrder, content) { prefs.favoriteOrder.mapNotNull { content.entry(it) } }
    if (saved.isEmpty()) {
        Column(Modifier.fillMaxSize().background(Grace.Night)) {
            ScreenHeader("Favorites")
            Box(Modifier.fillMaxSize().padding(bottom = bottomInset), contentAlignment = Alignment.Center) {
                EmptyState(
                    Icons.Outlined.FavoriteBorder,
                    "Nothing saved yet",
                    "Tap Save on any verse and it will be kept here for you.",
                ) {
                    OutlinedButton(onClick = onBrowse) { Text("Browse wallpapers", color = Grace.GoldSoft) }
                }
            }
        }
        return
    }
    LazyVerticalGrid(
        columns = GridCells.Adaptive(150.dp),
        modifier = Modifier.fillMaxSize().background(Grace.Night),
        contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = bottomInset + 16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item(span = { GridItemSpan(maxLineSpan) }) {
            ScreenHeader("Favorites", if (saved.size == 1) "1 saved verse" else "${saved.size} saved verses", horizontal = 8.dp)
        }
        items(saved, key = { it.id }) { entry ->
            WallpaperThumb(entry, isFavorite = true) { actions.open(entry, null) }
        }
    }
}

@Composable
fun HistoryScreen(content: Content, prefs: PrefsState, actions: EntryActions, bottomInset: Dp) {
    val today = LocalDate.now()
    val days = remember(today, prefs.firstUseEpochDay) {
        DailySchedule.historyDates(today, LocalDate.ofEpochDay(prefs.firstUseEpochDay))
    }
    LazyColumn(
        Modifier.fillMaxSize().background(Grace.Night),
        contentPadding = PaddingValues(bottom = bottomInset + 16.dp),
    ) {
        item { ScreenHeader("History", "Every day’s grace, kept for you") }
        items(days, key = { it.toEpochDay() }) { day ->
            val entry = DailySchedule.entryFor(day, content.entries)
            HistoryRow(day, entry, entry.id in prefs.favorites) { actions.open(entry, day.toString()) }
        }
    }
}

@Composable
private fun HistoryRow(day: LocalDate, entry: GraceEntry, isFavorite: Boolean, onClick: () -> Unit) {
    val image by rememberAssetImage(entry.thumbPath, 216)
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 24.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .width(62.dp)
                .aspectRatio(9f / 20f)
                .clip(RoundedCornerShape(12.dp))
                .background(Grace.SurfaceHigh),
        ) {
            image?.let { Image(it, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop) }
        }
        Spacer(Modifier.width(18.dp))
        Column(Modifier.weight(1f)) {
            Text(dayLabel(day).uppercase(), style = MaterialTheme.typography.labelSmall, color = Grace.Gold)
            Spacer(Modifier.height(6.dp))
            Text(
                "“${entry.verse}”",
                fontFamily = Scripture,
                fontStyle = FontStyle.Normal,
                fontSize = 19.sp,
                lineHeight = 24.sp,
                color = Grace.Ink,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(Modifier.height(6.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(entry.reference, style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
                if (isFavorite) {
                    Spacer(Modifier.width(8.dp))
                    Icon(Icons.Filled.Favorite, contentDescription = "Saved", tint = Grace.Gold, modifier = Modifier.size(13.dp))
                }
            }
        }
    }
}
