using System;
using System.Collections.Generic;
using System.Text;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class Controle
    {
        private static int[] conjuntoM = { 10, 20, 50 };

        private static double[] conjuntoR = { 1.5, 2.0 };

        private static double[] conjuntoAlpha = { 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 };

        public static void Executar()
        {
            Random rand = new Random();
            string caminhoSalvamento = @"C:\Projetos\Teoria da Computação\Resultados_Tarefas"; //Preencher com o caminho de salvamento desejado
            Directory.CreateDirectory(caminhoSalvamento);
            string nomeArquivo = $"Resultado_{DateTime.Now:dd_MM_yyyy_HH_mm}.txt";
            string caminhoCompleto = Path.Combine(caminhoSalvamento, nomeArquivo);

            using (var writer = new StreamWriter(caminhoCompleto, append: false, encoding: Encoding.UTF8))
            {
                writer.WriteLine("Heurística, n, m, replicação, tempo, iterações, makespan inicial, makespan final, parametro\n");

                //Gera dados para primeira melhora, refazendo paramentros aleatorios por execução
                for (int i = 0; i <= 10; i++)
                {

                    int m = conjuntoM[rand.Next(0, 3)];
                    double r = conjuntoR[rand.Next(0, 2)];

                    int n = (int)Math.Pow(m, r);

                    ResolucaoTarefas resolucao = new ResolucaoTarefas(n, m);
                    resolucao.ExecutaPrimeiraEscolha();

                    writer.WriteLine($"Monótona primeira escolha, {n}, {m}, {i}, {resolucao.Tempo} ms, {resolucao.Iteracoes}, {resolucao.MakespanInicial}, {resolucao.MakespanFinal}, NA");
                }

                writer.WriteLine("\n");

                //Gera dados para melhor melhora, refazendo paramentros aleatorios por execução
                for (int i = 0; i <= 10; i++)
                {

                    int m = conjuntoM[rand.Next(0, 3)];
                    double r = conjuntoR[rand.Next(0, 2)];

                    int n = (int)Math.Pow(m, r);

                    ResolucaoTarefas resolucao = new ResolucaoTarefas(n, m);
                    resolucao.ExecutaMelhorEscolha();

                    writer.WriteLine($"Monótona melhor escolha, {n}, {m}, {i}, {resolucao.Tempo} ms, {resolucao.Iteracoes}, {resolucao.MakespanInicial}, {resolucao.MakespanFinal}, NA");
                }

                writer.WriteLine("\n");

                //Gera dados para BLM randomizada, refazendo paramentros aleatorios por execução
                for (int i = 0; i <= 10; i++)
                {

                    int m = conjuntoM[rand.Next(0, 3)];
                    double r = conjuntoR[rand.Next(0, 2)];
                    double alpha = conjuntoAlpha[rand.Next(0, 9)]; //Define a chance de movimento randomizado

                    int n = (int)Math.Pow(m, r); 

                    ResolucaoTarefas resolucao = new ResolucaoTarefas(n, m, alpha);
                    resolucao.ExecutaBuscaMonotonaRandomizada();

                    writer.WriteLine($"BLM randomizada, {n}, {m}, {i}, {resolucao.Tempo} ms, {resolucao.Iteracoes}, {resolucao.MakespanInicial}, {resolucao.MakespanFinal}, {resolucao.parametroAlpha}");
                }

            }
            Console.WriteLine("Resultados gerados!");

        }
    }
}
