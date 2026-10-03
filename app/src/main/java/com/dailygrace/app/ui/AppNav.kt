package com.dailygrace.app.ui

import android.widget.Toast
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.actions.Sharer
import com.dailygrace.app.data.Content
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.ui.components.GraceIcons
import com.dailygrace.app.ui.screens.ApplyWallpaperScreen
import com.dailygrace.app.ui.screens.EntryDetailScreen
import com.dailygrace.app.ui.screens.FavoritesScreen
import com.dailygrace.app.ui.screens.HistoryScreen
import com.dailygrace.app.ui.screens.LoadingScreen
import com.dailygrace.app.ui.screens.LoadErrorScreen
import com.dailygrace.app.ui.screens.PrayerScreen
import com.dailygrace.app.ui.screens.SettingsScreen
import com.dailygrace.app.ui.screens.TodayScreen
import com.dailygrace.app.ui.screens.WallpapersScreen
import com.dailygrace.app.ui.theme.Grace
import kotlinx.coroutines.launch

object Routes {
    const val TODAY = "today"
    const val WALLPAPERS = "wallpapers"
    const val FAVORITES = "favorites"
    const val HISTORY = "history"
    const val PRAYER = "prayer"
    const val SETTINGS = "settings"
    const val ENTRY = "entry/{id}?date={date}"
    const val APPLY = "apply/{id}"

    fun entry(id: String, date: String? = null) = if (date == null) "entry/$id" else "entry/$id?date=$date"
    fun apply(id: String) = "apply/$id"
}

private data class Tab(val route: String, val label: String, val icon: ImageVector)

private val tabs = listOf(
    Tab(Routes.TODAY, "Today", GraceIcons.Today),
    Tab(Routes.WALLPAPERS, "Wallpapers", GraceIcons.Wallpapers),
    Tab(Routes.FAVORITES, "Favorites", Icons.Outlined.FavoriteBorder),
    Tab(Routes.HISTORY, "History", GraceIcons.History),
    Tab(Routes.PRAYER, "Prayer", GraceIcons.Prayer),
)

private sealed interface Load {
    data object Loading : Load
    data class Ready(val content: Content) : Load
    data class Failed(val message: String) : Load
}

/** Actions every page needs, wired once. */
class EntryActions(
    val toggleFavorite: (GraceEntry) -> Unit,
    val setWallpaper: (GraceEntry) -> Unit,
    val share: (GraceEntry) -> Unit,
    val open: (GraceEntry, String?) -> Unit,
)

@Composable
fun DailyGraceRoot() {
    val app = LocalContext.current.applicationContext as DailyGraceApp
    var retry by remember { mutableIntStateOf(0) }
    val load by produceState<Load>(Load.Loading, retry) {
        value = Load.Loading
        value = try {
            Load.Ready(app.content.content())
        } catch (e: Exception) {
            Load.Failed(e.message ?: "Something went wrong")
        }
    }
    when (val l = load) {
        Load.Loading -> LoadingScreen()
        is Load.Failed -> LoadErrorScreen(l.message) { retry++ }
        is Load.Ready -> GraceNavHost(l.content)
    }
}

@Composable
private fun GraceNavHost(content: Content) {
    val context = LocalContext.current
    val app = context.applicationContext as DailyGraceApp
    val prefs by app.prefs.state.collectAsStateWithLifecycle()
    val nav = rememberNavController()
    val scope = rememberCoroutineScope()
    val backStack by nav.currentBackStackEntryAsState()
    val route = backStack?.destination?.route
    val showTabs = tabs.any { it.route == route } || route == null

    val systemBottom = WindowInsets.navigationBars.asPaddingValues().calculateBottomPadding()
    val tabBarHeight = 64.dp
    val tabInset: Dp = systemBottom + tabBarHeight

    val actions = EntryActions(
        toggleFavorite = { app.prefs.toggleFavorite(it.id) },
        setWallpaper = { nav.navigate(Routes.apply(it.id)) },
        share = { entry ->
            scope.launch {
                Sharer.share(context, entry, content.translation.code).onFailure {
                    Toast.makeText(context, "Couldn’t prepare the image to share", Toast.LENGTH_SHORT).show()
                }
            }
        },
        open = { entry, date -> nav.navigate(Routes.entry(entry.id, date)) },
    )

    Box(Modifier.fillMaxSize().background(Grace.Night)) {
        NavHost(
            navController = nav,
            startDestination = Routes.TODAY,
            enterTransition = { fadeIn(tween(260)) },
            exitTransition = { fadeOut(tween(200)) },
            popEnterTransition = { fadeIn(tween(260)) },
            popExitTransition = { fadeOut(tween(200)) },
        ) {
            composable(Routes.TODAY) {
                TodayScreen(content, prefs, actions, bottomInset = tabInset, onSettings = { nav.navigate(Routes.SETTINGS) })
            }
            composable(Routes.WALLPAPERS) {
                WallpapersScreen(content, actions, bottomInset = tabInset, prefs = prefs)
            }
            composable(Routes.FAVORITES) {
                FavoritesScreen(content, prefs, actions, bottomInset = tabInset, onBrowse = { switchTab(nav, Routes.WALLPAPERS) })
            }
            composable(Routes.HISTORY) {
                HistoryScreen(content, prefs, actions, bottomInset = tabInset)
            }
            composable(Routes.PRAYER) {
                PrayerScreen(content, bottomInset = tabInset)
            }
            composable(Routes.SETTINGS) {
                SettingsScreen(content, prefs, onBack = { nav.popBackStack() })
            }
            composable(
                Routes.ENTRY,
                arguments = listOf(
                    navArgument("id") { type = NavType.StringType },
                    navArgument("date") { type = NavType.StringType; nullable = true; defaultValue = null },
                ),
                enterTransition = { slideInVertically(tween(320)) { it / 10 } + fadeIn(tween(320)) },
                popExitTransition = { slideOutVertically(tween(240)) { it / 10 } + fadeOut(tween(240)) },
            ) { entry ->
                val id = entry.arguments?.getString("id").orEmpty()
                val date = entry.arguments?.getString("date")
                EntryDetailScreen(content, id, date, prefs, actions, bottomInset = systemBottom, onBack = { nav.popBackStack() })
            }
            composable(
                Routes.APPLY,
                arguments = listOf(navArgument("id") { type = NavType.StringType }),
                enterTransition = { slideInVertically(tween(320)) { it / 8 } + fadeIn(tween(320)) },
                popExitTransition = { slideOutVertically(tween(240)) { it / 8 } + fadeOut(tween(240)) },
            ) { entry ->
                val id = entry.arguments?.getString("id").orEmpty()
                ApplyWallpaperScreen(content, id, prefs, onBack = { nav.popBackStack() })
            }
        }

        AnimatedVisibility(
            visible = showTabs,
            modifier = Modifier.align(Alignment.BottomCenter),
            enter = fadeIn(tween(200)),
            exit = fadeOut(tween(150)),
        ) {
            TabBar(route) { switchTab(nav, it) }
        }
    }
}

private fun switchTab(nav: NavHostController, route: String) {
    nav.navigate(route) {
        popUpTo(nav.graph.findStartDestination().id) { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}

@Composable
private fun TabBar(current: String?, onSelect: (String) -> Unit) {
    Box(
        Modifier
            .fillMaxWidth()
            .background(Brush.verticalGradient(listOf(Grace.Night.copy(alpha = 0.0f), Grace.Night.copy(alpha = 0.94f), Grace.Night)))
            .navigationBarsPadding()
            .height(64.dp),
    ) {
        Row(
            Modifier.fillMaxSize().padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.SpaceAround,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            tabs.forEach { tab ->
                val selected = tab.route == (current ?: Routes.TODAY)
                val tint = if (selected) Grace.Gold else Color.White.copy(alpha = 0.62f)
                Column(
                    Modifier
                        .clip(RoundedCornerShape(16.dp))
                        .clickable(
                            interactionSource = null,
                            indication = null,
                            role = Role.Tab,
                            onClickLabel = tab.label,
                        ) { if (!selected) onSelect(tab.route) }
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Icon(tab.icon, contentDescription = null, tint = tint, modifier = Modifier.size(23.dp))
                    Spacer(Modifier.height(4.dp))
                    Text(tab.label, style = MaterialTheme.typography.labelMedium, color = tint)
                    Spacer(Modifier.height(3.dp))
                    Box(
                        Modifier
                            .size(4.dp)
                            .clip(CircleShape)
                            .background(if (selected) Grace.Gold else Color.Transparent)
                    )
                }
            }
        }
    }
}
