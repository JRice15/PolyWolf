//
// VoteReasonMap.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// A mapping between agent and its declared vote with reason.
    /// </summary>
    class VoteReasonMap : Dictionary<Agent, (Agent Target, Content Reason)>
    {
        /// <summary>
        /// Registers voter ,vote target and reason.
        /// </summary>
        /// <param name="voter">The voter.</param>
        /// <param name="target">The vote target.</param>
        /// <param name="reason">the reason for voting.</param>
        /// <returns>true if the voter is not Agent.NONE.</returns>
        /// <remarks>If target is Agent.NONE, the voter's entry is removed.</remarks>
        public bool Put(Agent voter, Agent target, Content reason)
        {
            if (voter == Agent.NONE)
            {
                return false;
            }
            if (target == Agent.NONE)
            {
                Remove(voter);
            }
            else
            {
                this[voter] = (target, reason);
            }
            return true;
        }

        /// <summary>
        /// Registers voter ,vote target without reason.
        /// </summary>
        /// <param name="voter">The voter.</param>
        /// <param name="target">The vote target.</param>
        /// <returns>true always.</returns>
        public bool Put(Agent voter, Agent target) => Put(voter, target, Content.Empty);

        /// <summary>
        /// Registers utterance of vote and reason.
        /// </summary>
        /// <param name="utterance">The utterance of vote.</param>
        /// <param name="reason">The reason for vote.</param>
        /// <returns>true if the utterance's Topic is VOTE.</returns>
        public bool Put(Content utterance, Content reason) => utterance.Topic == Topic.VOTE && Put(utterance.Subject, utterance.Target, reason);

        /// <summary>
        /// Registers the utterance.
        /// </summary>
        /// <param name="utterance">The utterance concerning vote.</param>
        /// <returns>true if the utterance is concerning vote.</returns>
        public bool Put(Content utterance)
        {
            if (utterance.Topic == Topic.VOTE)
            {
                return Put(utterance, Content.Empty);
            }
            else if (utterance.Operator == Operator.BECAUSE && utterance.ContentList[1].Topic == Topic.VOTE)
            {
                return Put(utterance.ContentList[1], utterance.ContentList[0]);
            }
            return false;
        }

        /// <summary>
        /// Returns the number of votes the vote target got.
        /// </summary>
        /// <param name="target">The vote target.</param>
        /// <returns>The number of votes.</returns>
        public int GetVoteCount(Agent target) => Keys.Where(a => this[a].Target == target).Count();

        /// <summary>
        /// The total number of votes.
        /// </summary>
        public int VoteCount => Count;

        /// <summary>
        /// The vote targets.
        /// </summary>
        public List<Agent> Targets => Values.Select(t => t.Target).Distinct().ToList();

        /// <summary>
        /// Returns a list of agents sorted in descending order of vote count.
        /// </summary>
        /// <param name="excludes">The list of agents to exclude from the list to be returned.</param>
        /// <returns>A list of agents.</returns>
        public List<Agent> GetOrderedList(List<Agent> excludes)
            => Targets.Where(t => !excludes.Contains(t)).OrderByDescending(a => GetVoteCount(a)).ToList();

        /// <summary>
        /// Returns a list of agents sorted in descending order of vote count.
        /// </summary>
        /// <param name="excludes">The array of agents to exclude from the list to be returned.</param>
        /// <returns>A list of agents.</returns>
        public List<Agent> GetOrderedList(params Agent[] excludes) => GetOrderedList(excludes.ToList());

        /// <summary>
        /// Returns the agent's vote target.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>The vote target.</returns>
        /// <remarks>Returns Agent.NONE if not found.</remarks>
        public Agent GetTarget(Agent agent) => TryGetValue(agent, out var t) ? t.Target : Agent.NONE;

        /// <summary>
        /// Returns the agent's vote reason.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>The vote reason.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content GetReason(Agent agent) => TryGetValue(agent, out var t) ? t.Reason : Content.Empty;

        /// <summary>
        /// Returns the reason of the agents's voting for the target.
        /// </summary>
        /// <param name="agent">The voter.</param>
        /// <param name="target">The voted agent.</param>
        /// <returns>The reason.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content GetReason(Agent agent, Agent target) => GetTarget(agent) == target ? GetReason(target) : Content.Empty;

        /// <summary>
        /// The largest of the targets' vote count.
        /// </summary>
        public int MaxVoteCount => Targets.Select(a => GetVoteCount(a)).OrderByDescending(c => c).FirstOrDefault();

        /// <summary>
        /// A list of agents that get the max number of votes.
        /// </summary>
        public List<Agent> Winners => Targets.Where(a => GetVoteCount(a) == MaxVoteCount).ToList();

    }

}
