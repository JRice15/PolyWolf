//
// UtteranceStatstics.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// Utterance statistics.
    /// </summary>
    class UtteranceStatistics
    {
        /// <summary>
        /// Initializes absolute count with the initial value.
        /// </summary>
        /// <param name="initialValue">The initial value.</param>
        public UtteranceStatistics(double initialValue)
        {
            for (var turn = 0; turn < Feature.NumTurns; turn++)
            {
                for (var iTopic = 0; iTopic < Feature.NumTopics; iTopic++)
                {
                    AbsoluteMatrix[turn, iTopic] = initialValue;
                }
            }
        }

        /// <summary>
        /// Sets value.
        /// </summary>
        /// <param name="turn">The turn.</param>
        /// <param name="topic">The topic.</param>
        /// <param name="value">The value.</param>
        /// <returns>true on success.</returns>
        public bool Set(int turn, Topic topic, double value)
        {
            if (turn < 0 || turn >= Feature.NumTurns || !Feature.TopicIntMap.TryGetValue(topic, out int v) || AbsoluteMatrix[turn, v] == value)
            {
                return false;
            }
            AbsoluteMatrix[turn, Feature.TopicIntMap[topic]] = value;
            return true;
        }

        /// <summary>
        /// Gets value.
        /// </summary>
        /// <param name="turn">The turn.</param>
        /// <param name="topic">The topic.</param>
        /// <returns>0 if not found.</returns>
        public double Get(int turn, Topic topic)
        {
            if (turn < 0 || turn >= Feature.NumTurns || !Feature.TopicIntMap.ContainsKey(topic))
            {
                return 0;
            }
            return AbsoluteMatrix[turn, Feature.TopicIntMap[topic]];
        }

        /// <summary>
        /// Increments value.
        /// </summary>
        /// <param name="turn">The turn.</param>
        /// <param name="topic">The topic.</param>
        /// <returns>true on success.</returns>
        public bool Increment(int turn, Topic topic)
        {
            if (turn < 0 || turn >= Feature.NumTurns || !Feature.TopicIntMap.ContainsKey(topic))
            {
                return false;
            }
            AbsoluteMatrix[turn, Feature.TopicIntMap[topic]]++;
            return true;
        }

        /// <summary>
        /// Add statistics.
        /// </summary>
        /// <param name="addition">The addition.</param>
        /// <returns>true on success.</returns>
        public bool Add(double[,] addition)
        {
            if (addition.GetLength(0) != Feature.NumTurns || addition.GetLength(1) != Feature.NumTopics)
            {
                return false;
            }
            for (var turn = 0; turn < Feature.NumTurns; turn++)
            {
                for (var iTopic = 0; iTopic < Feature.NumTopics; iTopic++)
                {
                    AbsoluteMatrix[turn, iTopic] += addition[turn, iTopic];
                }
            }
            return true;
        }

        /// <summary>
        /// Relative frequency matrix.
        /// </summary>
        public double[,] RelativeMatrix
        {
            get
            {
                var relative = new double[Feature.NumTurns, Feature.NumTopics];
                for (int turn = 0; turn < Feature.NumTurns; turn++)
                {
                    double sum = 0;
                    for (var iTopic = 0; iTopic < Feature.NumTopics; iTopic++)
                    {
                        sum += AbsoluteMatrix[turn, iTopic];
                    }
                    for (var iTopic = 0; iTopic < Feature.NumTopics; iTopic++)
                    {
                        relative[turn, iTopic] = sum == 0 ? 0 : AbsoluteMatrix[turn, iTopic] / sum;
                    }
                }
                return relative;
            }
        }

        /// <summary>
        /// Relative frequency vector.
        /// </summary>
        public double[] RelativeVector => RelativeMatrix.Cast<double>().ToArray();

        /// <summary>
        /// Frequency matrix.
        /// </summary>
        public double[,] AbsoluteMatrix { get; } = new double[Feature.NumTurns, Feature.NumTopics];

        /// <summary>
        /// Frequency vector.
        /// </summary>
        public double[] AbsoluteVector => AbsoluteMatrix.Cast<double>().ToArray();
    }
}
