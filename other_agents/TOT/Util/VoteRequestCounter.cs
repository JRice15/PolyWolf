//
// VoteRequestCounter.cs
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
    /// Counts requests for vote.
    /// </summary>
    class VoteRequestCounter: Dictionary<Agent, Agent>
    {
        /// <summary>
        /// Add a content.
        /// </summary>
        /// <param name="content">The content to be added.</param>
        /// <returns>true if the content is concerning vote request.</returns>
        public bool Add(Content content)
        {
            if (content.Operator == Operator.REQUEST && content.ContentList[0].Topic == Topic.VOTE)
            {
                this[content.Subject] = content.ContentList[0].Target;
                return true;
            }
            return false;
        }

        /// <summary>
        /// Returns the number of requests of vote for the target.
        /// </summary>
        /// <param name="target">The target.</param>
        /// <returns>The number of requests.</returns>
        public int GetCount(Agent target) => Values.Where(a => a == target).Count();

        /// <summary>
        /// The targets.
        /// </summary>
        public List<Agent> Targets => Values.Distinct().ToList();

        /// <summary>
        /// The largest of the numner of request for the target. 
        /// </summary>
        public int MaxCount => Targets.Select(a => GetCount(a)).OrderByDescending(c => c).FirstOrDefault();

        /// <summary>
        /// The list of agents that get the max number of requests.
        /// </summary>
        public List<Agent> TopAgentList => Targets.Where(a => GetCount(a) == MaxCount).ToList();

    }

}
