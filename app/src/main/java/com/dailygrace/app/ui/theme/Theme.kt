package com.dailygrace.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp
import com.dailygrace.app.R

object Grace {
    val Night = Color(0xFF0F1218)
    val Surface = Color(0xFF171B23)
    val SurfaceHigh = Color(0xFF1F2430)
    val Line = Color(0x1FFFFFFF)
    val Gold = Color(0xFFE2C188)
    val GoldSoft = Color(0xFFF1DDB4)
    val Ink = Color(0xFFF4EFE6)
    val Muted = Color(0xFFA9A39A)
    val Faint = Color(0xFF6E6A64)
}

val Scripture = FontFamily(
    Font(R.font.cormorant_garamond_500, FontWeight.Medium),
    Font(R.font.cormorant_garamond_600, FontWeight.SemiBold),
    Font(R.font.cormorant_garamond_500_italic, FontWeight.Medium, FontStyle.Italic),
)

val Interface = FontFamily(
    Font(R.font.inter_400, FontWeight.Normal),
    Font(R.font.inter_500, FontWeight.Medium),
    Font(R.font.inter_600, FontWeight.SemiBold),
)

private val GraceTypography = Typography(
    displaySmall = TextStyle(fontFamily = Scripture, fontWeight = FontWeight.Medium, fontSize = 34.sp, lineHeight = 40.sp),
    headlineMedium = TextStyle(fontFamily = Scripture, fontWeight = FontWeight.SemiBold, fontSize = 30.sp, lineHeight = 36.sp),
    headlineSmall = TextStyle(fontFamily = Scripture, fontWeight = FontWeight.SemiBold, fontSize = 24.sp, lineHeight = 30.sp),
    titleLarge = TextStyle(fontFamily = Scripture, fontWeight = FontWeight.SemiBold, fontSize = 22.sp, lineHeight = 28.sp),
    titleMedium = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Medium, fontSize = 16.sp, lineHeight = 22.sp),
    titleSmall = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Medium, fontSize = 14.sp, lineHeight = 20.sp),
    bodyLarge = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 25.sp),
    bodyMedium = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Normal, fontSize = 14.sp, lineHeight = 21.sp),
    bodySmall = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Normal, fontSize = 12.sp, lineHeight = 17.sp),
    labelLarge = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Medium, fontSize = 14.sp, letterSpacing = 0.02.em),
    labelMedium = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Medium, fontSize = 12.sp, letterSpacing = 0.04.em),
    labelSmall = TextStyle(fontFamily = Interface, fontWeight = FontWeight.Medium, fontSize = 11.sp, letterSpacing = 0.14.em),
)

private val GraceColors = darkColorScheme(
    primary = Grace.Gold,
    onPrimary = Color(0xFF1E1709),
    primaryContainer = Color(0xFF3A3020),
    onPrimaryContainer = Grace.GoldSoft,
    secondary = Grace.GoldSoft,
    onSecondary = Color(0xFF1E1709),
    background = Grace.Night,
    onBackground = Grace.Ink,
    surface = Grace.Surface,
    onSurface = Grace.Ink,
    surfaceVariant = Grace.SurfaceHigh,
    onSurfaceVariant = Grace.Muted,
    surfaceContainer = Grace.Surface,
    surfaceContainerHigh = Grace.SurfaceHigh,
    surfaceContainerHighest = Color(0xFF282E3B),
    outline = Color(0x33FFFFFF),
    outlineVariant = Grace.Line,
)

@Composable
fun DailyGraceTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = GraceColors, typography = GraceTypography, content = content)
}
