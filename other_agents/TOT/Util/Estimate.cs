//
// Estimate.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// Class representing a role estimate and its reason.
    /// </summary>
    class Estimate : IEquatable<Estimate>
    {
        /// <summary>
        /// Constant representing an empty estimate.
        /// </summary>
        public static readonly Estimate Empty = new Estimate(Agent.NONE, Agent.NONE);

        /// <summary>
        /// Parses a sentence and returns estimates in the sentence.
        /// </summary>
        /// <param name="content">The sentence to be parsed.</param>
        /// <returns>A list of estimates.</returns>
        /// <remarks>Returns an empty list if there is no estimate in the sentence.</remarks>
        public static List<Estimate> ParseContent(Content content)
        {
            var estimateList = new List<Estimate>();
            if (content.Topic == Topic.ESTIMATE)
            {
                estimateList.Add(new Estimate(content.Subject, content.Target, content.Role));
            }
            else if (content.Operator == Operator.AND || content.Operator == Operator.OR || content.Operator == Operator.XOR)
            {
                foreach (var c in content.ContentList.Where(c => c.Topic == Topic.ESTIMATE))
                {
                    estimateList.Add(new Estimate(c.Subject, c.Target, c.Role));
                }
            }
            else if (content.Operator == Operator.BECAUSE)
            {
                Content reason = content.ContentList[0];
                List<Estimate> estimates = ParseContent(content.ContentList[1]);
                estimates.ForEach(e => e.AddReason(reason));
                estimateList.AddRange(estimates);
            }
            return estimateList;
        }

        HashSet<Role> roles = new HashSet<Role>();
        HashSet<Content> reasons = new HashSet<Content>();

        /// <summary>
        /// Estimating agent.
        /// </summary>
        public Agent Estimator { get; }

        /// <summary>
        /// Estimated agent.
        /// </summary>
        public Agent Estimated { get; }

        /// <summary>
        /// Constructs an Estimate.
        /// </summary>
        /// <param name="estimator">The estimating agent.</param>
        /// <param name="estimated">The estimated agent.</param>
        /// <param name="roles">The estimated roles.</param>
        public Estimate(Agent estimator, Agent estimated, params Role[] roles)
        {
            Estimator = estimator;
            Estimated = estimated;
            roles.ToList().ForEach(r => AddRole(r));
        }

        /// <summary>
        /// Adds an estimated role to the existings.
        /// </summary>
        /// <param name="role">The role.</param>
        public bool AddRole(Role role) => roles.Add(role);

        /// <summary>
        /// Sets unique estimated role.
        /// </summary>
        /// <param name="role">The role.</param>
        public void SetUniqueRole(Role role)
        {
            roles.Clear();
            roles.Add(role);
        }

        /// <summary>
        /// Adds a reason to the existings.
        /// </summary>
        /// <param name="reason">The reason.</param>
        public void AddReason(Content reason) => reasons.Add(reason);

        /// <summary>
        /// Returns whether or not this estimate is about the role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>true if this estimate is about the role.</returns>
        public bool HasRole(Role role) => roles.Contains(role);

        /// <summary>
        /// Returns whether or not this estimate has the reason specified.
        /// </summary>
        /// <param name="reason">The reason.</param>
        /// <returns>true if this estimate has the reason.</returns>
        public bool HasReason(Content reason) => reasons.Contains(reason);

        /// <summary>
        /// Returns this estimate in the form of Content.
        /// </summary>
        /// <returns>An Content representing this estimate.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content ToContent()
        {
            Content content = GetEstimateContent();
            if (content == Content.Empty)
            {
                return Content.Empty;
            }
            Content reason = GetReasonContent();
            return reason == Content.Empty ? content : new Content(new BecauseContentBuilder(Estimator, reason, content));
        }

        /// <summary>
        /// Returns the estimates about multiple roles in a form of XOR Content.
        /// </summary>
        /// <returns>An ESTIMATE Content in case of single role, otherwise, a XOR Content omitting the third and following ones.</returns>
        /// <remarks>Returns Content.Empty if not found.</remarks>
        public Content GetEstimateContent()
        {
            var contents = roles.Select(r => new Content(new EstimateContentBuilder(Estimator, Estimated, r)));
            return contents.Count() switch
            {
                0 => Content.Empty,
                1 => contents.First(),
                _ => new Content(new XorContentBuilder(Estimator, contents.First(), contents.ElementAt(1))),
            };
        }

        /// <summary>
        /// Returns the reasons of this estimate in a form of AND Content.
        /// </summary>
        /// <returns>An ESTIMATE Content in case of single reason, otherwise, a AND Content.</returns>
        /// <remarks>Returns Content.Empty if there is no reason.</remarks>
        public Content GetReasonContent()
        {
            return reasons.Count() switch
            {
                0 => Content.Empty,
                1 => reasons.First(),
                _ => new Content(new AndContentBuilder(Estimator, reasons.ToArray())),
            };
        }

        public bool Equals(Estimate other) => ReferenceEquals(this, other) || (GetType() == other.GetType() && ToContent() == other.ToContent());

        public override bool Equals(object obj) => obj is Estimate estimate && Equals(estimate);

        public override int GetHashCode() => ToContent().GetHashCode();

        /// <summary>
        /// Equality operator.
        /// </summary>
        /// <param name="lhs">Left hand side.</param>
        /// <param name="rhs">Right hand side.</param>
        /// <returns>true if its oprands are equal.</returns>
        public static bool operator ==(Estimate lhs, Estimate rhs) => lhs.Equals(rhs);

        /// <summary>
        /// Inequality operator.
        /// </summary>
        /// <param name="lhs">Left hand side.</param>
        /// <param name="rhs">Right hand side.</param>
        /// <returns>true if its oprands are not equal.</returns>
        public static bool operator !=(Estimate lhs, Estimate rhs) => !(lhs == rhs);

    }

}
