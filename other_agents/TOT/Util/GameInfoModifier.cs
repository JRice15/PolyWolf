//
// GameInfoModifier.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using AIWolf.Server;
using System.Collections.Generic;

namespace TOT2021
{
    /// <summary>
    /// Manipulates GameInfo.
    /// </summary>
    class GameInfoModifier : GameInfo
    {
        /// <summary>
        /// Construct GameInfoModifier with a GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public GameInfoModifier(IGameInfo gameInfo)
        {
            Day = gameInfo.Day;
            Agent = gameInfo.Agent;
            MediumResult = gameInfo.MediumResult;
            DivineResult = gameInfo.DivineResult;
            ExecutedAgent = gameInfo.ExecutedAgent;
            LatestExecutedAgent = gameInfo.LatestExecutedAgent;
            AttackedAgent = gameInfo.AttackedAgent;
            CursedFox = gameInfo.CursedFox;
            GuardedAgent = gameInfo.GuardedAgent;
            VoteList = new List<Vote>(gameInfo.VoteList);
            LatestVoteList = new List<Vote>(gameInfo.LatestVoteList);
            AttackVoteList = new List<Vote>(gameInfo.AttackVoteList);
            LatestAttackVoteList = new List<Vote>(gameInfo.LatestAttackVoteList);
            TalkList = new List<Talk>(gameInfo.TalkList);
            WhisperList = new List<Whisper>(gameInfo.WhisperList);
            StatusMap = new Dictionary<Agent, Status>(gameInfo.StatusMap);
            RoleMap = new Dictionary<Agent, Role>(gameInfo.RoleMap);
            RemainTalkMap = new Dictionary<Agent, int>(gameInfo.RemainTalkMap);
            RemainWhisperMap = new Dictionary<Agent, int>(gameInfo.RemainWhisperMap);
            LastDeadAgentList = new List<Agent>(gameInfo.LastDeadAgentList);
            ExistingRoleList = new List<Role>(gameInfo.ExistingRoleList);
        }

        /// <summary>
        /// Sets role.
        /// </summary>
        /// <param name="role">The role</param>
        /// <returns>The modified GameInfoModifier.</returns>
        public GameInfoModifier SetFakeRole(Role role)
        {
            var map = new Dictionary<Agent, Role>(RoleMap)
            {
                [Agent] = role
            };
            RoleMap = map;
            return this;
        }

        /// <summary>
        /// Sets divine result.
        /// </summary>
        /// <param name="judge">The divine result.</param>
        /// <returns>The modified GameInfoModifier.</returns>
        public GameInfoModifier SetDivineResult(Judge judge)
        {
            DivineResult = judge;
            return this;
        }

        /// <summary>
        /// Sets medium result.
        /// </summary>
        /// <param name="judge">The medium result.</param>
        /// <returns>The modified GameInfoModifier.</returns>
        public GameInfoModifier SetMediumResult(Judge judge)
        {
            MediumResult = judge;
            return this;
        }
    }
}
