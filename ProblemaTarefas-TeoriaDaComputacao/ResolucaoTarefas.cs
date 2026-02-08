using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class ResolucaoTarefas
    {
        public double Tempo { get; private set; }
        public int Iteracoes { get; private set; } = 0;
        public int MakespanInicial { get; private set; }
        public int MakespanFinal { get; private set; }

        private Maquina[] _maquinas = new Maquina[1];

        public ResolucaoTarefas(int tarefas, int maquinas)
        {
            Tempo = 0;
            Iteracoes = 0;
            _maquinas = new Maquina[maquinas];
            for(int i = 0; i < maquinas; i++)
                _maquinas[i] = new Maquina();

            GerarTarefas(tarefas);
        }

        private void GerarTarefas(int n)
        {
            Random rand = new Random();

            for (int i = 0; i < n; i++)
            {
                int t = rand.Next(1, 100);
                _maquinas[0].AdicionarTarefa(t);
            }
            MakespanInicial = _maquinas[0].TempoEstimado;
        } 


        public void ExecutaMelhorEscolha()
        {
            Stopwatch sw = Stopwatch.StartNew();
            bool continuar = true;

            while (continuar)
            {
                Maquina? maquinaSpan = null;
                Maquina? melhorEscolha = null;
                foreach (var maquina in _maquinas)
                {
                    if(maquinaSpan == null || maquina.TempoEstimado > maquinaSpan.TempoEstimado)
                        maquinaSpan = maquina;
                    
                    if(melhorEscolha == null || maquina.TempoEstimado < melhorEscolha.TempoEstimado && !maquina.Equals(maquinaSpan))
                        melhorEscolha = maquina;
                }
         
                if(maquinaSpan!.Tarefas.Count > 0 && melhorEscolha!.TempoEstimado + maquinaSpan.Tarefas.Peek() < maquinaSpan.TempoEstimado)
                {
                    int tarefa = maquinaSpan.RetiraTarefa();
                    melhorEscolha!.AdicionarTarefa(tarefa);
                    Iteracoes++;
                }
                else
                {
                    continuar = false;
                    MakespanFinal = maquinaSpan.TempoEstimado;
                }
            }
            sw.Stop();
            Tempo = sw.Elapsed.TotalMicroseconds;
        }
    }
}
