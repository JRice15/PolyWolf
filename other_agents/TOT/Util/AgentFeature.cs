//
// AgentFeature.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using System;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// Container of agent features.
    /// </summary>
    class AgentFeature : List<double>
    {
        /// <summary>
        /// Feature array converted to an array of integers.
        /// </summary>
        public int[] IntArray => this.Select(d => Convert.ToInt32(d)).ToArray();

        /// <summary>
        /// This own value when regarded as a binary number.
        /// </summary>
        public int Bin => Convert.ToInt32(string.Join("", this.Select(d => d == 0 ? "0" : "1").ToArray()), 2);

        /// <summary>
        /// Clone of this.
        /// </summary>
        public AgentFeature Clone => new AgentFeature(this);

        /// <summary>
        /// Constructs an AgentFeature with an enumerator of features.
        /// </summary>
        /// <param name="feature">The enumerator of feature.</param>
        public AgentFeature(IEnumerable<double> feature) : base(feature) { }
    }
}
