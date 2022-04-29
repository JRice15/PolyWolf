//
// BasePlayer5.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class BasePlayer5 : BasePlayer
    {
        Dictionary<Agent, double> agent2WinRate = new Dictionary<Agent, double>();
        Dictionary<Agent, Role> bestRoleAssignment = new Dictionary<Agent, Role>();

        public BasePlayer5(MetaInfo metaInfo) : base(metaInfo) { }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            bestRoleAssignment.Clear();
            foreach (var a in Others)
            {
                agent2WinRate[a] = GameCount == 0 ? 0 : (double)GetWinCount(a) / GameCount;
                bestRoleAssignment[a] = Role.UNC;
            }
        }

        /// <summary>
        /// Searches the best role assignment excluding the specified agents from the specified role.
        /// </summary>
        /// <param name="fromRole">The specified role.</param>
        /// <param name="excludedAgents">The agents to be excluded from the role above.</param>
        protected void SearchAssignment(Role fromRole, IEnumerable<Agent> excludedAgents)
        {
            var candidatesMap = new Dictionary<Role, IEnumerable<Agent>>();
            foreach (var r in new Role[] { Role.WEREWOLF, Role.VILLAGER, Role.SEER, Role.POSSESSED })
            {
                if (r != fromRole)
                {
                    candidatesMap[r] = Others;
                }
                else
                {
                    candidatesMap[r] = Others.Where(a => !excludedAgents.Contains(a));
                }
            }
            double bestValue = 0.0;
            switch (MyRole)
            {
                case Role.WEREWOLF:
                    foreach (var seer in candidatesMap[Role.SEER])
                    {
                        foreach (var possessed in candidatesMap[Role.POSSESSED].Where(a => a != seer))
                        {
                            var (assignment, value) = EvalAssignment(seer: seer, possessed: possessed);
                            if (value > bestValue)
                            {
                                bestValue = value;
                                bestRoleAssignment = assignment;
                            }
                        }
                    }
                    break;
                case Role.VILLAGER:
                    foreach (var seer in candidatesMap[Role.SEER])
                    {
                        foreach (var werewolf in candidatesMap[Role.WEREWOLF].Where(a => a != seer))
                        {
                            foreach (var possessed in candidatesMap[Role.POSSESSED].Where(a => a != seer && a != werewolf))
                            {
                                var (assignment, value) = EvalAssignment(seer: seer, possessed: possessed, werewolf: werewolf);
                                if (value > bestValue)
                                {
                                    bestValue = value;
                                    bestRoleAssignment = assignment;
                                }
                            }
                        }
                    }
                    break;
                case Role.SEER:
                    foreach (var werewolf in candidatesMap[Role.WEREWOLF])
                    {
                        foreach (var possessed in candidatesMap[Role.POSSESSED].Where(a => a != werewolf))
                        {
                            var (assignment, value) = EvalAssignment(possessed: possessed, werewolf: werewolf);
                            if (value > bestValue)
                            {
                                bestValue = value;
                                bestRoleAssignment = assignment;
                            }
                        }
                    }
                    break;
                case Role.POSSESSED:
                    foreach (var seer in candidatesMap[Role.SEER])
                    {
                        foreach (var werewolf in candidatesMap[Role.WEREWOLF].Where(a => a != seer))
                        {
                            var (assignment, value) = EvalAssignment(seer: seer, werewolf: werewolf);
                            if (value > bestValue)
                            {
                                bestValue = value;
                                bestRoleAssignment = assignment;
                            }
                        }
                    }
                    break;
                default:
                    break;
            }
        }

        (Dictionary<Agent, Role>, double) EvalAssignment(Agent seer = default!, Agent possessed = default!, Agent werewolf = default!)
        {
            var assignment = Others.ToDictionary(a => a, a => a == seer ? Role.SEER : a == possessed ? Role.POSSESSED : a == werewolf ? Role.WEREWOLF : Role.VILLAGER);
            return (assignment, assignment.Keys.Select(a => GetProbOf(a, assignment[a])).Sum());
        }

        protected Role GetRoleAssignmentOf(Agent agent)
        {
            SearchAssignment(Role.UNC, new Agent[0]);
            return bestRoleAssignment[agent];
        }

        /// <summary>
        /// Returns a list of agents assigned to the role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <param name="excludedAgents">The agents to be excluded from the returned list.</param>
        /// <returns>An empty list if not found.</returns>
        public List<Agent> GetAgentsAssignedTo(Role role, params Agent[] excludedAgents)
        {
            SearchAssignment(role, excludedAgents);
            return bestRoleAssignment.Keys.Where(a => bestRoleAssignment[a] == role).ToList();
        }

        protected double GetRateOf(Agent agent) => agent2WinRate[agent];

        /// <summary>
        /// Returns a fake GameInfo of the fake role having a fake divination result, from true GameInfo.
        /// </summary>
        /// <param name="gameInfo">The true GameInfo.</param>
        /// <param name="fakeRole">The fake role.</param>
        /// <param name="fakeDivination">The fake divination.</param>
        /// <returns></returns>
        protected IGameInfo GetFakeGameInfo(IGameInfo gameInfo, Role fakeRole, Judge fakeDivination)
        {
            return new GameInfoModifier(gameInfo).SetFakeRole(fakeRole).SetDivineResult(fakeDivination);
        }
    }
}
