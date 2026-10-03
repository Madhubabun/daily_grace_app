package com.dailygrace.app.ui.screens

import android.widget.Toast
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.actions.WallpaperApplier
import com.dailygrace.app.actions.WallpaperDestination
import com.dailygrace.app.actions.physicalScreenSize
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.PrefsState
import com.dailygrace.app.image.WallpaperFit
import com.dailygrace.app.render.GraceRenderer
import com.dailygrace.app.render.RenderTarget
import com.dailygrace.app.ui.components.EmptyState
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Interface
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

private enum class PreviewMode { HOME, LOCK }

private sealed interface ApplyState {
    data object Idle : ApplyState
    data object Working : ApplyState
    data object Done : ApplyState
}

/**
 * Set Wallpaper: a live preview on a phone frame shaped exactly like this phone's screen, then
 * Home / Lock / Both. The preview is rendered by the same code that renders the real wallpaper.
 */
@Composable
fun ApplyWallpaperScreen(content: Content, id: String, prefs: PrefsState, onBack: () -> Unit) {
    val context = LocalContext.current
    val app = context.applicationContext as DailyGraceApp
    val entry = content.entry(id)
    if (entry == null) {
        Box(Modifier.fillMaxSize().background(Grace.Night), contentAlignment = Alignment.Center) {
            EmptyState(GraceIcons.Wallpapers, "Not found", "This wallpaper is no longer in the app.") {
                OutlinedButton(onClick = onBack) { Text("Go back") }
            }
        }
        return
    }

    val (screenW, screenH) = remember { physicalScreenSize(context) }
    var includeVerse by rememberSaveable { mutableStateOf(prefs.wallpaperIncludesVerse) }
    var mode by rememberSaveable { mutableStateOf(PreviewMode.LOCK) }
    var state by remember { mutableStateOf<ApplyState>(ApplyState.Idle) }
    val scope = rememberCoroutineScope()

    val preview by produceState<ImageBitmap?>(null, entry.id, includeVerse) {
        value = withContext(Dispatchers.Default) {
            val art = app.images.loadFull(entry.imagePath) ?: return@withContext null
            // Half resolution is plenty for the preview and keeps it quick.
            val bmp = GraceRenderer.render(context, art, entry, screenW / 2, screenH / 2, RenderTarget.PREVIEW, includeVerse)
            art.recycle()
            bmp.asImageBitmap()
        }
    }

    val fitNote = remember(screenW, screenH) {
        val crop = WallpaperFit.crop(1440, 3200, screenW, screenH, 0.5f, entry.focusY)
        val kept = (WallpaperFit.safeZoneCoverage(1440, 3200, crop) * 100).toInt()
        "Fitted to your $screenW × $screenH screen · no stretching · safe zone $kept% kept"
    }

    fun applyTo(destination: WallpaperDestination) {
        if (state == ApplyState.Working) return
        state = ApplyState.Working
        scope.launch {
            val result = WallpaperApplier.apply(context, entry, destination, includeVerse)
            if (result.isSuccess) {
                state = ApplyState.Done
                val where = when (destination) {
                    WallpaperDestination.HOME -> "home screen"
                    WallpaperDestination.LOCK -> "lock screen"
                    WallpaperDestination.BOTH -> "home and lock screens"
                }
                Toast.makeText(context, "Set on your $where", Toast.LENGTH_SHORT).show()
                delay(900)
                onBack()
            } else {
                state = ApplyState.Idle
                Toast.makeText(
                    context,
                    result.exceptionOrNull()?.message ?: "The wallpaper couldn’t be set",
                    Toast.LENGTH_LONG,
                ).show()
            }
        }
    }

    Column(
        Modifier
            .fillMaxSize()
            .background(Grace.Night)
            .statusBarsPadding()
            .navigationBarsPadding(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(Modifier.fillMaxWidth().height(56.dp)) {
            IconButton(onClick = onBack, modifier = Modifier.align(Alignment.CenterStart).padding(start = 4.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Grace.Ink)
            }
            Column(Modifier.align(Alignment.Center), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("SET WALLPAPER", style = MaterialTheme.typography.labelSmall, color = Grace.GoldSoft)
                Text(entry.reference, style = MaterialTheme.typography.bodySmall, color = Grace.Muted)
            }
        }

        BoxWithConstraints(Modifier.weight(1f).fillMaxWidth().padding(vertical = 8.dp), contentAlignment = Alignment.Center) {
            val aspect = screenW.toFloat() / screenH
            val frameH = minOf(maxHeight, maxWidth * 0.62f / aspect)
            val frameW = frameH * aspect
            val shape = RoundedCornerShape(frameW * 0.11f)
            Box(
                Modifier
                    .width(frameW)
                    .height(frameH)
                    .clip(shape)
                    .background(Color.Black)
                    .border(5.dp, Color(0xFF2A2F3A), shape),
            ) {
                val alpha by animateFloatAsState(if (preview != null) 1f else 0f, tween(400), label = "preview")
                preview?.let {
                    Image(it, contentDescription = "Wallpaper preview", modifier = Modifier.fillMaxSize().alpha(alpha), contentScale = ContentScale.FillBounds)
                }
                if (preview == null) {
                    CircularProgressIndicator(Modifier.align(Alignment.Center).size(28.dp), color = Grace.Gold, strokeWidth = 2.dp)
                }
                when (mode) {
                    PreviewMode.LOCK -> LockOverlay(frameW.value)
                    PreviewMode.HOME -> HomeOverlay()
                }
                AnimatedVisibility(state == ApplyState.Done, enter = fadeIn(), exit = fadeOut(), modifier = Modifier.align(Alignment.Center)) {
                    Box(
                        Modifier.size(64.dp).clip(CircleShape).background(Grace.Gold),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(Icons.Filled.Check, contentDescription = "Done", tint = Grace.Night, modifier = Modifier.size(34.dp))
                    }
                }
            }
        }

        Text(
            fitNote,
            style = MaterialTheme.typography.bodySmall,
            color = Grace.Faint,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 24.dp),
        )
        Spacer(Modifier.height(12.dp))

        Row(
            Modifier.padding(horizontal = 20.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Segmented(mode) { mode = it }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Verse", style = MaterialTheme.typography.labelLarge, color = Grace.Ink)
                Spacer(Modifier.width(8.dp))
                Switch(
                    checked = includeVerse,
                    onCheckedChange = { includeVerse = it },
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
        Spacer(Modifier.height(14.dp))

        val busy = state != ApplyState.Idle
        Column(Modifier.padding(horizontal = 20.dp).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedButton(
                    onClick = { applyTo(WallpaperDestination.HOME) },
                    enabled = !busy,
                    modifier = Modifier.weight(1f).height(50.dp),
                ) { Text("Set as Home Screen", color = Grace.Ink, maxLines = 1, fontSize = 13.sp) }
                OutlinedButton(
                    onClick = { applyTo(WallpaperDestination.LOCK) },
                    enabled = !busy,
                    modifier = Modifier.weight(1f).height(50.dp),
                ) { Text("Set as Lock Screen", color = Grace.Ink, maxLines = 1, fontSize = 13.sp) }
            }
            Button(
                onClick = { applyTo(WallpaperDestination.BOTH) },
                enabled = !busy,
                modifier = Modifier.fillMaxWidth().height(54.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Grace.Gold, contentColor = Grace.Night),
            ) {
                if (state == ApplyState.Working) {
                    CircularProgressIndicator(Modifier.size(20.dp), color = Grace.Night, strokeWidth = 2.dp)
                    Spacer(Modifier.width(10.dp))
                    Text("Setting wallpaper…")
                } else {
                    Text("Set as Both", fontWeight = FontWeight.SemiBold)
                }
            }
        }
        Spacer(Modifier.height(14.dp))
    }
}

@Composable
private fun Segmented(mode: PreviewMode, onChange: (PreviewMode) -> Unit) {
    val shape = RoundedCornerShape(50)
    Row(
        Modifier.clip(shape).background(Grace.Surface).border(1.dp, Grace.Line, shape).padding(3.dp),
    ) {
        listOf(PreviewMode.LOCK to "Lock", PreviewMode.HOME to "Home").forEach { (m, label) ->
            val selected = m == mode
            Text(
                label,
                style = MaterialTheme.typography.labelLarge,
                color = if (selected) Grace.Night else Grace.Ink.copy(alpha = 0.8f),
                modifier = Modifier
                    .clip(shape)
                    .background(if (selected) Grace.GoldSoft else Color.Transparent)
                    .clickable { onChange(m) }
                    .padding(horizontal = 16.dp, vertical = 8.dp),
            )
        }
    }
}

/** A simple lock-screen clock so the user can judge how the verse sits under it. */
@Composable
private fun LockOverlay(frameWidthDp: Float) {
    val now = remember { java.time.LocalTime.now() }
    val date = remember { LocalDate.now().format(DateTimeFormatter.ofPattern("EEE, MMMM d", Locale.getDefault())) }
    Column(Modifier.fillMaxWidth().padding(top = (frameWidthDp * 0.16f).dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(Icons.Filled.Lock, contentDescription = null, tint = Color.White.copy(alpha = 0.8f), modifier = Modifier.size((frameWidthDp * 0.05f).dp))
        Spacer(Modifier.height((frameWidthDp * 0.02f).dp))
        Text(
            String.format(Locale.getDefault(), "%d:%02d", if (now.hour % 12 == 0) 12 else now.hour % 12, now.minute),
            fontFamily = Interface,
            fontWeight = FontWeight.Normal,
            fontSize = (frameWidthDp * 0.2f).sp,
            color = Color.White.copy(alpha = 0.92f),
        )
        Text(date, fontFamily = Interface, fontSize = (frameWidthDp * 0.045f).sp, color = Color.White.copy(alpha = 0.85f))
    }
}

/** App icons and a dock, drawn as soft placeholders. */
@Composable
private fun HomeOverlay() {
    BoxWithConstraints(Modifier.fillMaxSize()) {
        val icon = maxWidth * 0.14f
        val gap = maxWidth * 0.08f
        Column(
            Modifier.align(Alignment.BottomCenter).padding(bottom = maxHeight * 0.04f),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            repeat(2) {
                Row(horizontalArrangement = Arrangement.spacedBy(gap)) {
                    repeat(4) { Box(Modifier.size(icon).clip(RoundedCornerShape(icon * 0.3f)).background(Color.White.copy(alpha = 0.22f))) }
                }
                Spacer(Modifier.height(gap))
            }
            Spacer(Modifier.height(gap * 0.5f))
            Row(
                Modifier.clip(RoundedCornerShape(icon * 0.5f)).background(Color.White.copy(alpha = 0.12f)).padding(icon * 0.18f),
                horizontalArrangement = Arrangement.spacedBy(gap),
            ) {
                repeat(4) { Box(Modifier.size(icon).clip(RoundedCornerShape(icon * 0.3f)).background(Color.White.copy(alpha = 0.3f))) }
            }
        }
    }
}
