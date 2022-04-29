//
// Medium.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class Medium : Villager
    {
        int coDate;
        bool hasCo;
        int myIdentHead;

        public Medium(MetaInfo metaInfo) : base(metaInfo) { }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            coDate = 3;
            hasCo = false;
            myIdentHead = 0;
        }

        public override string Talk()
        {
            if (!hasCo && (Date >= coDate || IsCo(Role.MEDIUM) || FoundWolf))
            {
                TalkCo(Role.MEDIUM);
                hasCo = true;
            }
            if (hasCo)
            {
                var nextHead = MyIdentifications.Count;
                var idents = new List<Judge>();
                for (var i = nextHead - 1; i >= myIdentHead; i--)
                {
                    idents.Add(MyIdentifications[i]);
                }
                idents.ForEach(j => TalkIdentified(j.Target, j.Result));
                List<Content> contents = idents.Select(j => DayContent(Me, j.Day, IdentContent(Me, j.Target, j.Result))).ToList();
                contents.ForEach(c => EnqueueTalk(c));
                if (contents.Count > 1)
                {
                    EnqueueTalk(AndContent(Me, contents.ToArray()));
                }
                myIdentHead = nextHead;
            }
            return base.Talk();
        }

    }
}
