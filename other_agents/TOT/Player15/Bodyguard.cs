//
// Bodyguard.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    class Bodyguard : Villager
    {
        public Bodyguard(MetaInfo metaInfo) : base(metaInfo) { }

        public override Agent Guard() => AliveOthers.OrderByDescending(a => GuardEval(a)).First();

        private double GuardEval(Agent agent) => GetProbOf(agent, Role.VILLAGER) + GetProbOf(agent, Role.SEER) + GetProbOf(agent, Role.MEDIUM)
                - GetProbOf(agent, Role.POSSESSED) - GetProbOf(agent, Role.WEREWOLF)
                + (GetCoRoleOf(agent) == Role.SEER ? 1.0 : 0.0) + (IsFakeSeer(agent) ? -2.0 : 0.0)
                + (GetCoRoleOf(agent) == Role.MEDIUM ? 1.0 : 0.0) + (IsFakeMedium(agent) ? -2.0 : 0.0)
                + 3 * GetWinCount(agent) / (GameCount + 0.01);
    }
}
