# coding: utf-8
from numpy import array,full,logical_or,where,ndenumerate
from itertools import izip,combinations

class Picross:
    box = 'o'
    empty = 'x'
    init = ' '
    NORMAL,HINT,ILLEGAL = range(3)

    def __init__(self,R,C):
        self.Grid = full((R,C),Picross.init,'a1')
        self.RC = R,C
        self.Bars = [[] for _ in range(R+C)]
        self.Cands = [[] for _ in range(R+C)]

    def enumerate(self):
        return ndenumerate(self.Grid)

    def Std(self, i):
        return self.Grid[i,:] if i < self.RC[0] else self.Grid[:,i-self.RC[0]]

    def Next(self):
        if Picross.init in self.Grid:
            for i in range(sum(self.RC)):
                status, s = self.Common(i)
                if status == Picross.HINT:
                    std = self.Std(i)
                    diff = where(std != s)[0]
                    std[:] = s
                    self.Screen(i)
                    if i < self.RC[0]:
                        for j in diff:
                            self.Screen(self.RC[0]+j)
                        return [((i,j),std[j]) for j in diff]
                    else:
                        for j in diff:
                            self.Screen(j)
                        return [((j,i-self.RC[0]),std[j]) for j in diff]
        return []

    def Common(self, i):
        cands = self.Cands[i]
        std = self.Std(i)
        if cands:
            s = array(cands[0])
            s[logical_or.reduce(cands!=s)] = Picross.init
            if (std != s).any():
                return Picross.HINT,s
            else:
                return Picross.NORMAL,None
        else:
            return Picross.ILLEGAL,None

    def Screen(self, i):
        cands = self.Cands[i]
        std = self.Std(i)
        cands[:] = [cand for cand in cands
                    if logical_or(std==Picross.init, cand==std).all()]

    def Candid(self, i): # generate candidates
        cands = self.Cands[i]
        std = self.Std(i)
        length = self.RC[i < self.RC[0]]
        # each hint is considered as a bar
        bars = self.Bars[i]
        # the leftover are considered as foos
        fooLen = length - sum(bars)
        # bar the foos with no more than one bar between two foos
        # 隔板法
        cands[:] = []
        for barLocs in combinations(range(fooLen+1), len(bars)):
            cand = full(length,Picross.empty, 'a1')
            # 0 1 2   3   4 5 6   7    8 -> bar location
            #  x x x ooo x x x x oooo x  -> x = foo, o...o = bar
            #  0 1 2 345 6 7 8 9 abcd e
            offset = 0
            for barLoc, barLen in izip(barLocs, bars):
                barLoc += offset
                cand[barLoc:barLoc+barLen] = Picross.box
                offset += barLen
            cands.append(cand)
