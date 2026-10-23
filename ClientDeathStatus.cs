namespace PsychologHan;

internal static class ClientDeathStatus
{
    internal const string TreatmentCancelled = "Treatment is cancelled due to client's death.";

    internal static bool IsKnownDead(global::GameState state, string client)
    {
        if (state == null)
        {
            return false;
        }

        switch (client)
        {
            case "Vera":
                return state.notifiedDeathVera;
            case "Jaden":
                return state.notifiedDeathJaden;
            case "Joe":
                return state.notifiedDeathJoe;
            case "Ashley":
                // Older builds never set notifiedDeathAshley at dialogue 37080.
                // Her death is decided at 21160, BEFORE the police reveal it.
                // The next map (21300, timeCode 2130) is after that conversation.
                return state.notifiedDeathAshley ||
                    ((state.ashleyDied || state.killedAshley) && state.timeCode >= 2130);
            case "Deborah":
                // Both builds mark her death at 42115, the police death notice;
                // only the updated build also sets notifiedDeathDeborah there.
                return state.notifiedDeathDeborah || state.deborahDied || state.killedDeborah;
            default:
                return false;
        }
    }
}
