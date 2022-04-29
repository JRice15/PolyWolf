//
// AttackVoteReasonMap.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;

namespace TOT2021
{
    /// <summary>
    ///  A mapping between agent and its declared attack vote with reason.
    /// </summary>
    class AttackVoteReasonMap : VoteReasonMap
    {
        /// <summary>
        /// Associates the utterance of attack vote with the reason.
        /// </summary>
        /// <param name="utterance">The utterance of attack vote.</param>
        /// <param name="reason">The reason for attack vote.</param>
        /// <returns>true if the utterance's Topic is ATTACK.</returns>
        public new bool Put(Content utterance, Content reason) => utterance.Topic == Topic.ATTACK && Put(utterance.Subject, utterance.Target, reason);

        /// <summary>
        /// Registers the utterance.
        /// </summary>
        /// <param name="utterance">The utterance concerning attack vote.</param>
        /// <returns>true if the utterance is concerning attack vote.</returns>
        public new bool Put(Content utterance)
        {
            if (utterance.Topic == Topic.ATTACK)
            {
                return Put(utterance, Content.Empty);
            }
            else if (utterance.Operator == Operator.BECAUSE && utterance.ContentList[1].Topic == Topic.ATTACK)
            {
                return Put(utterance.ContentList[1], utterance.ContentList[0]);
            }
            return false;
        }

    }
}
