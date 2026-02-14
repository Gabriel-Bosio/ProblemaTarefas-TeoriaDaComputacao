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
            string caminhoSalvamento = @"C:\Projetos\Teoria da Computação\Resultados_Tarefas";
            Directory.CreateDirectory(caminhoSalvamento);
            string nomeArquivo = $"Resultado_{DateTime.Now:dd_MM_yyyy_HH_mm}.txt";
            string caminhoCompleto = Path.Combine(caminhoSalvamento, nomeArquivo);

            Console.WriteLine("Criando arquivo...");
            using (var writer = new StreamWriter(caminhoCompleto, append: false, encoding: Encoding.UTF8))
            {
                writer.WriteLine("Heurística, n, m, replicação, tempo, iterações, makespan inicial, makespan final, parametro\n");

                Console.WriteLine("Simulando buscas locais monótonas");
                for (int i = 0; i <= 10; i++)
                {

                    int m = conjuntoM[rand.Next(0, 3)];
                    double r = conjuntoR[rand.Next(0, 2)];

                    int n = (int)Math.Pow(m, r);

                    ResolucaoTarefas resolucao = new ResolucaoTarefas(n, m);
                    resolucao.ExecutaMelhorEscolha();

                    writer.WriteLine($"Monótona melhor escolha, {n}, {m}, {i}, {resolucao.Tempo} ms, {resolucao.Iteracoes}, {resolucao.MakespanInicial}, {resolucao.MakespanFinal}, NA");
                }

            }
            Console.WriteLine("Resultados gerados!");

        }
    }
}
