package com.dailygrace.app

import com.dailygrace.app.data.DailySchedule
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.data.VerseLayout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate

class DailyScheduleTest {
    private fun entries(n: Int) = (1..n).map {
        GraceEntry(
            id = "%03d".format(it), dateIndex = it, image = "wallpaper_%03d.jpg".format(it), verse = "v$it",
            reference = "r$it", theme = "", categories = emptyList(), reflection = null, prayer = null,
            layout = VerseLayout.BOTTOM, focusY = 0.5f, excerpt = false,
        )
    }

    @Test
    fun sameDayAlwaysGivesSameEntry() {
        val list = entries(29)
        val d = LocalDate.of(2026, 12, 25)
        assertEquals(DailySchedule.entryFor(d, list), DailySchedule.entryFor(d, list))
    }

    @Test
    fun anchorDayShowsFirstEntryAndNextDayTheSecond() {
        val list = entries(29)
        assertEquals("001", DailySchedule.entryFor(DailySchedule.ANCHOR, list).id)
        assertEquals("002", DailySchedule.entryFor(DailySchedule.ANCHOR.plusDays(1), list).id)
    }

    @Test
    fun cyclesAndHandlesDatesBeforeTheAnchor() {
        val list = entries(10)
        assertEquals("001", DailySchedule.entryFor(DailySchedule.ANCHOR.plusDays(10), list).id)
        assertEquals("010", DailySchedule.entryFor(DailySchedule.ANCHOR.minusDays(1), list).id)
    }

    @Test
    fun historyIsNewestFirstAndNeverEmpty() {
        val today = LocalDate.of(2026, 10, 3)
        val days = DailySchedule.historyDates(today, firstUse = today)
        assertEquals(today, days.first())
        assertEquals(14, days.size)
        assertTrue(days.zipWithNext().all { (a, b) -> a.minusDays(1) == b })
    }

    @Test
    fun historyKeepsEverythingSinceFirstUse() {
        val today = LocalDate.of(2027, 3, 1)
        val first = LocalDate.of(2026, 10, 3)
        val days = DailySchedule.historyDates(today, first)
        assertEquals(first, days.last())
    }
}
