using System;
using System.Collections.Generic;
using System.Text;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class Controle
    {
        private static int[] conjuntoM = { 10, 20, 50 };

        private static double[] conjuntoR = { 1.5, 2.0 };

        public static void Executar()
        {
            Random rand = new Random();
            Console.WriteLine("heuristica, n, m, replicação, tempo, iterações, makespan inicial, makespan final, parametro\n");

            for(int i = 0; i <= 10; i++)
            {
                
                int m = conjuntoM[rand.Next(0, 3)];
                double r = conjuntoR[rand.Next(0, 2)];

                int n = (int)Math.Pow(m, r);

                ResolucaoTarefas resolucao = new ResolucaoTarefas(n, m);
                resolucao.ExecutaMelhorEscolha();

                Console.WriteLine($"Monotona melhor escolha, {n}, {m}, {resolucao.Tempo} us, {resolucao.Iteracoes}, {resolucao.MakespanInicial}, {resolucao.MakespanFinal}, NA");
            }
        }
    }
}
