package com.dailygrace.app.ui.components

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.Layout
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.LineBreak
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.image.VerseStyle
import com.dailygrace.app.ui.theme.Grace
import com.dailygrace.app.ui.theme.Interface
import com.dailygrace.app.ui.theme.Scripture
import kotlin.math.roundToInt

/** The verse in quotes, with KJV "LORD" set in small capitals. */
fun scriptureText(verse: String, size: TextUnit): AnnotatedString = buildAnnotatedString {
    val q = VerseStyle.quoted(verse)
    append(q)
    for (r in VerseStyle.smallCapRanges(q)) {
        addStyle(SpanStyle(fontSize = size * VerseStyle.SMALL_CAP_SCALE), r.first, r.last + 1)
    }
}

private val softShadow = Shadow(Color(0x99000000), Offset(0f, 2f), 14f)

/**
 * Places the verse and reference over the artwork at the entry's layout band, with a scrim that
 * is only as dark as the artwork underneath needs. The block is clamped between [topLimit] and
 * [bottomLimit] (fractions of the height) so it never collides with the header or actions.
 */
@Composable
fun VerseOverlay(
    entry: GraceEntry,
    bandCenter: Float,
    width: Dp,
    modifier: Modifier = Modifier,
    topLimit: Float = 0.13f,
    bottomLimit: Float = 0.82f,
    animateIn: Boolean = true,
    sizeScale: Float = 1f,
) {
    val app = LocalContext.current.applicationContext as DailyGraceApp
    val lum by produceState(0.45f, entry.thumbPath, bandCenter) {
        value = app.images.bandLuminance(entry.thumbPath, bandCenter)
    }
    val scrimAlpha = VerseStyle.scrimAlpha(lum)

    val density = LocalDensity.current
    val verseSize = with(density) { (width * VerseStyle.verseSizeFraction(entry.verse) * sizeScale).toSp() }
    val refSize = with(density) { (width * VerseStyle.REFERENCE_SIZE_FRACTION * sizeScale).toSp() }
    val text = remember(entry.verse, verseSize) { scriptureText(entry.verse, verseSize) }

    val reveal = remember(entry.id) { Animatable(if (animateIn) 0f else 1f) }
    LaunchedEffect(entry.id) { reveal.animateTo(1f, tween(900)) }

    Layout(
        modifier = modifier.fillMaxSize(),
        content = {
            Box(
                Modifier
                    .fillMaxWidth()
                    .background(
                        Brush.verticalGradient(
                            0f to Color.Transparent,
                            0.3f to Color(0xFF080A10).copy(alpha = scrimAlpha),
                            0.7f to Color(0xFF080A10).copy(alpha = scrimAlpha),
                            1f to Color.Transparent,
                        )
                    )
            )
            Column(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = width * ((1f - VerseStyle.TEXT_WIDTH_FRACTION) / 2f))
                    .graphicsLayer {
                        alpha = reveal.value
                        translationY = (1f - reveal.value) * 24.dp.toPx()
                    },
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text(
                    text,
                    style = TextStyle(
                        fontFamily = Scripture,
                        fontWeight = FontWeight.Medium,
                        fontSize = verseSize,
                        lineHeight = verseSize * 1.16f,
                        color = Color.White,
                        textAlign = TextAlign.Center,
                        lineBreak = LineBreak.Heading,
                        shadow = softShadow,
                    ),
                )
                Spacer(Modifier.height(width * 0.05f))
                Text(
                    entry.reference.uppercase(),
                    style = TextStyle(
                        fontFamily = Interface,
                        fontWeight = FontWeight.Medium,
                        fontSize = refSize,
                        letterSpacing = 0.14.em,
                        color = Grace.GoldSoft,
                        textAlign = TextAlign.Center,
                        shadow = softShadow,
                    ),
                )
            }
        },
    ) { measurables, constraints ->
        val h = constraints.maxHeight
        val w = constraints.maxWidth
        val textPlaceable = measurables[1].measure(constraints.copy(minHeight = 0, minWidth = w))
        val block = textPlaceable.height
        val ideal = (h * bandCenter - block / 2f).roundToInt()
        val minTop = (h * topLimit).roundToInt()
        val maxTop = (h * bottomLimit).roundToInt() - block
        val top = if (maxTop < minTop) minTop else ideal.coerceIn(minTop, maxTop)
        val pad = (w * 0.24f).roundToInt()
        val scrimHeight = block + pad * 2
        val scrimPlaceable = measurables[0].measure(constraints.copy(minHeight = scrimHeight, maxHeight = scrimHeight, minWidth = w))
        layout(w, h) {
            scrimPlaceable.place(0, top - pad)
            textPlaceable.place(0, top)
        }
    }
}
