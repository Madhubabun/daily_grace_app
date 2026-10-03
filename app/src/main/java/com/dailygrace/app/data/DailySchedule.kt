package com.dailygrace.app.data

import java.time.LocalDate

/**
 * Deterministic day -> entry mapping. The same date always shows the same entry, on every
 * phone, with no server. Entries cycle in dateIndex order starting from [ANCHOR].
 */
object DailySchedule {
    /** The first day of the cycle shows the first entry (Psalm 23:1). */
    val ANCHOR: LocalDate = LocalDate.of(2026, 10, 3)

    fun indexFor(date: LocalDate, count: Int): Int {
        require(count > 0) { "No entries" }
        val days = date.toEpochDay() - ANCHOR.toEpochDay()
        return Math.floorMod(days, count.toLong()).toInt()
    }

    fun entryFor(date: LocalDate, entries: List<GraceEntry>): GraceEntry = entries[indexFor(date, entries.size)]

    /**
     * Days shown in History, newest first: everything since the user first opened the app,
     * and at least [minimumDays] so the list is never empty on day one.
     */
    fun historyDates(today: LocalDate, firstUse: LocalDate, minimumDays: Int = 14): List<LocalDate> {
        val earliest = minOf(firstUse, today.minusDays((minimumDays - 1).toLong()))
        val out = ArrayList<LocalDate>()
        var d = today
        while (!d.isBefore(earliest)) {
            out += d
            d = d.minusDays(1)
        }
        return out
    }
}
