from org.biofab.jython import FooInterface

from RBS_Calculator import RBS_Calculator
import os, math

class Foo(FooInterface):

        def __init__(self, data):
                self.data = data
                self.bar = "Floop"

        def add(self, n1, n2):
                return n1 + n2


	def get(self):
		return self.data + " | " + self.bar


        def rbs_calc(self, seq):

                os.putenv('NUPACKHOME', '/opt/nupack')

                start_range = [0, len(seq)]
                name = "no name"
                

                calcObj = RBS_Calculator(seq, start_range, name)
                calcObj.calc_dG()
                
                dG_total_list = calcObj.dG_total_list[:]
                start_pos_list = calcObj.start_pos_list[:]
                kinetic_score_list = calcObj.kinetic_score_list[:]
                
                txt = ""

                expr_list = []
                for dG in dG_total_list:
                        expr_list.append(calcObj.K * math.exp(-dG/calcObj.RT_eff))

                txt += str(len(expr_list))+"\n"
                for (expr,start_pos,ks) in zip(expr_list,start_pos_list,kinetic_score_list):
                        txt += str(start_pos)+" "+str(expr)+" "+str(ks)+"\n"

                return txt
