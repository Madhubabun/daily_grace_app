package com.dailygrace.app.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.outlined.Share
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.image.VerseStyle
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Scripture

data class MenuAction(val label: String, val onClick: () -> Unit)

/**
 * The immersive page used for Today, for history entries and for any wallpaper: the artwork
 * fills the screen with the verse over it; scrolling reveals the reflection and prayer.
 */
@Composable
fun GraceEntryPage(
    entry: GraceEntry,
    eyebrow: String,
    subtitle: String,
    isFavorite: Boolean,
    translationName: String,
    onToggleFavorite: () -> Unit,
    onSetWallpaper: () -> Unit,
    onShare: () -> Unit,
    bottomInset: Dp,
    modifier: Modifier = Modifier,
    motion: Boolean = true,
    onBack: (() -> Unit)? = null,
    menu: List<MenuAction> = emptyList(),
    extras: @Composable ColumnScope.() -> Unit = {},
) {
    val scroll = rememberScrollState()
    BoxWithConstraints(modifier.fillMaxSize().background(Grace.Night)) {
        val screenH = maxHeight
        val screenW = maxWidth
        val heroPx = with(LocalDensity.current) { screenH.toPx() }
        val progress = (scroll.value / (heroPx * 0.35f)).coerceIn(0f, 1f)

        Column(Modifier.fillMaxSize().verticalScroll(scroll)) {
            Box(Modifier.fillMaxWidth().height(screenH)) {
                ArtworkImage(entry, Modifier.fillMaxSize(), motion = motion, parallaxPx = scroll.value.toFloat())
                VerticalShade(Modifier.fillMaxWidth().height(160.dp), Color.Black.copy(alpha = 0.45f), Color.Transparent)
                VerticalShade(
                    Modifier.align(Alignment.BottomCenter).fillMaxWidth().height(screenH * 0.2f),
                    Color.Transparent, Grace.Night,
                )
                VerseOverlay(
                    entry = entry,
                    bandCenter = VerseStyle.screenBandCenter(entry.layout),
                    width = screenW,
                    bottomLimit = 1f - (bottomInset + 96.dp) / screenH,
                )
                ScrollHint(
                    Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = bottomInset + 78.dp)
                        .alpha(1f - progress),
                    hasMore = entry.reflection != null || entry.prayer != null,
                )
            }
            ReflectionSection(entry, translationName)
            extras()
            Spacer(Modifier.height(bottomInset + 96.dp))
        }

        // Header stays put and gains a backdrop as the page scrolls.
        Box(
            Modifier
                .fillMaxWidth()
                .background(Grace.Night.copy(alpha = 0.92f * ((scroll.value - heroPx * 0.75f) / (heroPx * 0.2f)).coerceIn(0f, 1f)))
                .statusBarsPadding()
                .height(60.dp)
        ) {
            if (onBack != null) {
                IconButton(onClick = onBack, modifier = Modifier.align(Alignment.CenterStart).padding(start = 4.dp)) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                }
            }
            Column(Modifier.align(Alignment.Center), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(eyebrow.uppercase(), style = MaterialTheme.typography.labelSmall, color = Grace.GoldSoft)
                if (subtitle.isNotEmpty()) {
                    Spacer(Modifier.height(2.dp))
                    Text(subtitle, style = MaterialTheme.typography.bodySmall, color = Color.White.copy(alpha = 0.78f))
                }
            }
            if (menu.isNotEmpty()) {
                var open by remember { mutableStateOf(false) }
                Box(Modifier.align(Alignment.CenterEnd).padding(end = 4.dp)) {
                    IconButton(onClick = { open = true }) {
                        Icon(Icons.Filled.MoreVert, contentDescription = "More", tint = Color.White)
                    }
                    DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
                        menu.forEach { item ->
                            DropdownMenuItem(text = { Text(item.label) }, onClick = { open = false; item.onClick() })
                        }
                    }
                }
            }
        }

        GraceActionBar(
            isFavorite = isFavorite,
            onFavorite = onToggleFavorite,
            onSetWallpaper = onSetWallpaper,
            onShare = onShare,
            compact = screenW < 370.dp,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = bottomInset + 14.dp),
        )
    }
}

@Composable
private fun ScrollHint(modifier: Modifier, hasMore: Boolean) {
    if (!hasMore) return
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Reflection & Prayer", style = MaterialTheme.typography.labelMedium, color = Color.White.copy(alpha = 0.7f))
        Icon(GraceIcons.ChevronDown, contentDescription = null, tint = Color.White.copy(alpha = 0.6f), modifier = Modifier.size(18.dp))
    }
}

@Composable
fun Eyebrow(text: String, icon: ImageVector? = null) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        if (icon != null) {
            Icon(icon, contentDescription = null, tint = Grace.Gold, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(8.dp))
        }
        Text(text.uppercase(), style = MaterialTheme.typography.labelSmall, color = Grace.Gold)
    }
}

@Composable
private fun ReflectionSection(entry: GraceEntry, translationName: String) {
    Column(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 28.dp)
            .padding(top = 8.dp),
    ) {
        entry.reflection?.let {
            Eyebrow("Today’s Reflection", GraceIcons.Cross)
            Spacer(Modifier.height(14.dp))
            Text(
                it,
                fontFamily = Scripture,
                fontStyle = FontStyle.Italic,
                fontSize = 23.sp,
                lineHeight = 31.sp,
                color = Grace.Ink,
            )
            Spacer(Modifier.height(30.dp))
        }
        entry.prayer?.let {
            HorizontalDivider(color = Grace.Line)
            Spacer(Modifier.height(28.dp))
            Eyebrow("Today’s Prayer", GraceIcons.Prayer)
            Spacer(Modifier.height(14.dp))
            Text(it, style = MaterialTheme.typography.bodyLarge, color = Grace.Ink.copy(alpha = 0.88f))
            Spacer(Modifier.height(30.dp))
        }
        HorizontalDivider(color = Grace.Line)
        Spacer(Modifier.height(18.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (entry.theme.isNotBlank()) {
                Text(
                    entry.theme,
                    style = MaterialTheme.typography.labelMedium,
                    color = Grace.GoldSoft,
                    modifier = Modifier
                        .clip(RoundedCornerShape(50))
                        .background(Grace.SurfaceHigh)
                        .padding(horizontal = 12.dp, vertical = 6.dp),
                )
                Spacer(Modifier.width(12.dp))
            }
            Text(
                "${entry.reference} · $translationName",
                style = MaterialTheme.typography.bodySmall,
                color = Grace.Muted,
            )
        }
    }
}

/** Save · Set Wallpaper · Share, on a quiet glass pill. */
@Composable
fun GraceActionBar(
    isFavorite: Boolean,
    onFavorite: () -> Unit,
    onSetWallpaper: () -> Unit,
    onShare: () -> Unit,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    val shape = RoundedCornerShape(32.dp)
    Row(
        modifier
            .clip(shape)
            .background(Color(0xCC12151D))
            .border(1.dp, Color.White.copy(alpha = 0.10f), shape)
            .padding(6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        val pop by animateFloatAsState(if (isFavorite) 1f else 0.92f, spring(dampingRatio = 0.35f, stiffness = 500f), label = "heart")
        GlassButton(
            icon = if (isFavorite) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder,
            label = if (isFavorite) "Saved" else "Save",
            tint = if (isFavorite) Grace.Gold else Color.White,
            iconScale = pop,
            showLabel = !compact,
            onClick = onFavorite,
        )
        Row(
            Modifier
                .clip(RoundedCornerShape(26.dp))
                .background(Brush.horizontalGradient(listOf(Color(0xFFEACB92), Color(0xFFD9B272))))
                .clickable(role = Role.Button, onClick = onSetWallpaper)
                .padding(horizontal = 16.dp, vertical = 13.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(GraceIcons.SetWallpaper, contentDescription = null, tint = Color(0xFF1E1709), modifier = Modifier.size(19.dp))
            Spacer(Modifier.width(8.dp))
            Text("Set Wallpaper", style = MaterialTheme.typography.labelLarge, color = Color(0xFF1E1709))
        }
        GlassButton(icon = Icons.Outlined.Share, label = "Share", tint = Color.White, showLabel = !compact, onClick = onShare)
    }
}

@Composable
private fun GlassButton(
    icon: ImageVector,
    label: String,
    tint: Color,
    onClick: () -> Unit,
    iconScale: Float = 1f,
    showLabel: Boolean = true,
) {
    Row(
        Modifier
            .clip(RoundedCornerShape(26.dp))
            .clickable(role = Role.Button, onClickLabel = label, onClick = onClick)
            .padding(horizontal = 11.dp, vertical = 13.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, contentDescription = if (showLabel) null else label, tint = tint, modifier = Modifier.size(19.dp).scale(iconScale))
        if (showLabel) {
            Spacer(Modifier.width(6.dp))
            Text(label, style = MaterialTheme.typography.labelLarge, color = tint)
        }
    }
}

/** Calm empty state used by Favorites and History. */
@Composable
fun EmptyState(icon: ImageVector, title: String, message: String, modifier: Modifier = Modifier, action: (@Composable () -> Unit)? = null) {
    Column(
        modifier.padding(horizontal = 40.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            Modifier.size(72.dp).clip(CircleShape).background(Grace.SurfaceHigh),
            contentAlignment = Alignment.Center,
        ) {
            Icon(icon, contentDescription = null, tint = Grace.Gold, modifier = Modifier.size(30.dp))
        }
        Spacer(Modifier.height(20.dp))
        Text(title, style = MaterialTheme.typography.headlineSmall, color = Grace.Ink, textAlign = TextAlign.Center)
        Spacer(Modifier.height(8.dp))
        Text(message, style = MaterialTheme.typography.bodyMedium, color = Grace.Muted, textAlign = TextAlign.Center)
        if (action != null) {
            Spacer(Modifier.height(22.dp))
            action()
        }
    }
}
