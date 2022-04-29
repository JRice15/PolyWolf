//
// MetaInfo.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;

namespace TOT2021
{
    /// <summary>
    /// Meta information.
    /// </summary>
    class MetaInfo
    {
        /// <summary>
        /// The number of games this player participated in.
        /// </summary>
        public int GameCount { get; private set; }

        Dictionary<Role, int> roleCountMap = new Dictionary<Role, int>();

        Dictionary<Agent, int> winCountMap = new Dictionary<Agent, int>();

        Dictionary<Agent, bool> ppAbility = new Dictionary<Agent, bool>();

        Dictionary<Role, RoleEstimator> estimatorMap = new Dictionary<Role, RoleEstimator>();

        /// <summary>
        /// Constructs a MetaInfo.
        /// </summary>
        public MetaInfo()
        {
            foreach (var r in new List<Role> { Role.WEREWOLF, Role.VILLAGER, Role.SEER, Role.POSSESSED, Role.MEDIUM, Role.BODYGUARD })
            {
                estimatorMap[r] = new RoleEstimator(r);
                roleCountMap[r] = 0;
            }
        }

        /// <summary>
        /// Initializes this using a GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public void Initialize(IGameInfo gameInfo)
        {
            foreach (var r in gameInfo.ExistingRoleList)
            {
                GetRoleEstimator(r).Initialize(gameInfo);
            }
        }

        /// <summary>
        /// Updates this using a GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public void Update(IGameInfo gameInfo)
        {
            foreach (var r in gameInfo.ExistingRoleList)
            {
                GetRoleEstimator(r).Update(gameInfo);
            }
        }

        /// <summary>
        /// Returns whether or not an agent can do PP.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent can do PP.</returns>
        public bool GetPpAbility(Agent agent) => ppAbility.TryGetValue(agent, out var ability) && ability;

        /// <summary>
        /// Sets whether or not a agent can do PP.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <param name="ability">Wheter or not the agent can do PP.</param>
        public void SetPpAbility(Agent agent, bool ability) => ppAbility[agent] = ability;

        /// <summary>
        /// Returns the number of times this player played the role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>The number of times.</returns>
        public int GetRoleCount(Role role) => roleCountMap[role];

        /// <summary>
        /// Increments the number of times this player played the role.
        /// </summary>
        /// <param name="role">The role.</param>
        public void IncrementRoleCount(Role role) => roleCountMap[role]++;

        /// <summary>
        /// Returns a estimator for a role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>The estimator for the role.</returns>
        public RoleEstimator GetRoleEstimator(Role role) => estimatorMap[role];

        /// <summary>
        /// Game end processing.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public void Finish(IGameInfo gameInfo)
        {
            foreach (var r in gameInfo.ExistingRoleList)
            {
                GetRoleEstimator(r).Finish();
            }
            GameCount++;
        }

        /// <summary>
        /// Returns the number of wins for a agent.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>The agent's number of wins.</returns>
        public int GetWinCount(Agent agent)
        {
            if (agent == Agent.NONE)
            {
                return 0;
            }
            if (!winCountMap.ContainsKey(agent))
            {
                winCountMap[agent] = 0;
            }
            return winCountMap[agent];
        }

        /// <summary>
        /// Increments the number of wins for a agent.
        /// </summary>
        /// <param name="agent">The agent.</param>
        public void IncrementWinCount(Agent agent)
        {
            if (agent == Agent.NONE)
            {
                return;
            }
            if (!winCountMap.ContainsKey(agent))
            {
                winCountMap[agent] = 1;
            }
            else
            {
                winCountMap[agent]++;
            }
        }

    }
}
