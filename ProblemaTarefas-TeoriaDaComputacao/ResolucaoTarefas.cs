using System;
using System.Collections.Generic;
using System.Text;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class ResolucaoTarefas
    {
        public int Tarefas { get; }
        public int Maquinas { get; }
        public double Tempo { get; }

        private Maquina[] _maquinas = new Maquina[1];

        public ResolucaoTarefas(int tarefas, int maquinas)
        {
            Tarefas = tarefas;
            Maquinas = maquinas;
            Tempo = 0;
            _maquinas = new Maquina[maquinas];

            GerarTarefas(tarefas);
        }

        private void GerarTarefas(int n)
        {
            Random rand = new Random();

            for (int i = 0; i < n; i++)
            {
                int t = rand.Next(1, 100);
                _maquinas[0].Tarefas.Push(t);
            }
        } 


        private void ExecutaMelhorEscolha()
        {
            int makespan = _maquinas.Max(m => m.TempoEstimado);
            bool continuar = true;


            while (continuar)
            {
                //foreach (var maquina in _maquinas)
                //{
                //    Maquina maquina = _maquinas.Max(maquina => maquina.TempoEstimado);
                //}
            }
        }
    }
}
