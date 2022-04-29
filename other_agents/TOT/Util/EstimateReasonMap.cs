//
// EatimateReasonMap.cs
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
    /// A mapping between agent and its estimate with reason.
    /// </summary>
    class EstimateReasonMap : Dictionary<Agent, Dictionary<Agent, Estimate>>
    {
        /// <summary>
        /// Registers an estimate.
        /// </summary>
        /// <param name="estimate">The Estimate to be registered.</param>
        /// <returns>true always.</returns>
        public bool Put(Estimate estimate)
        {
            this[estimate.Estimator] = new Dictionary<Agent, Estimate>() { [estimate.Estimated] = estimate };
            return true;
        }

        /// <summary>
        /// Registers the estimate contained in the utterance.
        /// </summary>
        /// <param name="content">The utterance.</param>
        /// <returns>true if any estimate found.</returns>
        public bool Put(Content content)
        {
            List<Estimate> estimates = Estimate.ParseContent(content);
            return estimates.Count > 0 && estimates.All(e => Put(e));
        }

        /// <summary>
        /// Returns the agent's estimate about the estimated agent in the form of Content.
        /// </summary>
        /// <param name="estimator">The agent which does estimate.</param>
        /// <param name="estimated">The estimated agent.</param>
        /// <returns>The estimate in the form of Content.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content GetContent(Agent estimator, Agent estimated) => GetEstimate(estimator, estimated).ToContent();

        /// <summary>
        /// Returns the agent's estimate about the estimated agent in the form of Estimate.
        /// </summary>
        /// <param name="estimator">The agent which does estimate.</param>
        /// <param name="estimated">The estimated agent.</param>
        /// <returns>The estimate in the form of Estimate.</returns>
        /// <remarks>Returns Estimate.EMPTY if not found.</remarks>
        public Estimate GetEstimate(Agent estimator, Agent estimated)
            => TryGetValue(estimator, out var a) && a.TryGetValue(estimated, out var b) ? b : Estimate.Empty;

        /// <summary>
        /// Returns the reason of the agent's estimate about the estimated agent.
        /// </summary>
        /// <param name="estimater">The agent which does estimate.</param>
        /// <param name="estimated">The estimated agent.</param>
        /// <returns>The reason in the form of Content.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content GetReason(Agent estimater, Agent estimated)
        {
            var content = GetContent(estimater, estimated);
            return content.Operator == Operator.BECAUSE ? content.ContentList[0] : Content.Empty;
        }

        /// <summary>
        /// Returns the agents estimated to be the role by the estimator agent.
        /// </summary>
        /// <param name="estimator">The estimator agent.</param>
        /// <param name="role">The estimated role.</param>
        /// <returns>The list of agents estimated to be the role.</returns>
        /// <remarks>Returns an empty list if no agent is found.</remarks>
        public List<Agent> GetEstimated(Agent estimator, Role role)
        {
            var agents = new HashSet<Agent>();
            if (TryGetValue(estimator, out var map))
            {
                foreach (var e in map.Values.Where(e => e.HasRole(role)))
                {
                    agents.Add(e.Estimated);
                }
            }
            return agents.ToList();
        }

    }

}
