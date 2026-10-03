package com.dailygrace.app.data

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDate

data class PrefsState(
    val favorites: Set<String>,
    /** Newest first. */
    val favoriteOrder: List<String>,
    val firstUseEpochDay: Long,
    val reminderEnabled: Boolean,
    val reminderHour: Int,
    val reminderMinute: Int,
    val reminderPromptDismissed: Boolean,
    val wallpaperIncludesVerse: Boolean,
    val gentleMotion: Boolean,
)

/** Everything the app remembers lives on the phone in one small SharedPreferences file. */
class UserPrefs(context: Context) {
    private val sp = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
    private val _state = MutableStateFlow(read())
    val state: StateFlow<PrefsState> = _state.asStateFlow()

    init {
        if (!sp.contains(KEY_FIRST_USE)) {
            sp.edit().putLong(KEY_FIRST_USE, LocalDate.now().toEpochDay()).apply()
            _state.value = read()
        }
    }

    private fun read(): PrefsState {
        val order = sp.getString(KEY_FAVORITES, "").orEmpty().split(',').filter { it.isNotBlank() }
        return PrefsState(
            favorites = order.toSet(),
            favoriteOrder = order,
            firstUseEpochDay = sp.getLong(KEY_FIRST_USE, LocalDate.now().toEpochDay()),
            reminderEnabled = sp.getBoolean(KEY_REMINDER, false),
            reminderHour = sp.getInt(KEY_HOUR, 7),
            reminderMinute = sp.getInt(KEY_MINUTE, 0),
            reminderPromptDismissed = sp.getBoolean(KEY_PROMPT_DISMISSED, false),
            wallpaperIncludesVerse = sp.getBoolean(KEY_WALLPAPER_VERSE, true),
            gentleMotion = sp.getBoolean(KEY_MOTION, true),
        )
    }

    private fun update(block: android.content.SharedPreferences.Editor.() -> Unit) {
        sp.edit().apply(block).apply()
        _state.value = read()
    }

    fun isFavorite(id: String) = id in _state.value.favorites

    fun toggleFavorite(id: String) {
        val order = _state.value.favoriteOrder
        val next = if (id in order) order - id else listOf(id) + order
        update { putString(KEY_FAVORITES, next.joinToString(",")) }
    }

    fun setReminder(enabled: Boolean) = update { putBoolean(KEY_REMINDER, enabled); putBoolean(KEY_PROMPT_DISMISSED, true) }
    fun setReminderTime(hour: Int, minute: Int) = update { putInt(KEY_HOUR, hour); putInt(KEY_MINUTE, minute) }
    fun dismissReminderPrompt() = update { putBoolean(KEY_PROMPT_DISMISSED, true) }
    fun setWallpaperIncludesVerse(value: Boolean) = update { putBoolean(KEY_WALLPAPER_VERSE, value) }
    fun setGentleMotion(value: Boolean) = update { putBoolean(KEY_MOTION, value) }

    companion object {
        const val FILE = "daily_grace"
        private const val KEY_FAVORITES = "favorites"
        private const val KEY_FIRST_USE = "first_use_epoch_day"
        private const val KEY_REMINDER = "reminder_enabled"
        private const val KEY_HOUR = "reminder_hour"
        private const val KEY_MINUTE = "reminder_minute"
        private const val KEY_PROMPT_DISMISSED = "reminder_prompt_dismissed"
        private const val KEY_WALLPAPER_VERSE = "wallpaper_includes_verse"
        private const val KEY_MOTION = "gentle_motion"
    }
}
