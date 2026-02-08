// See https://aka.ms/new-console-template for more information
Console.WriteLine("Hello, World!");


// Planejamento (Atualmente priorizxado a não monótona, veremos como incluir o outro algoritmo da melhor forma depois)

// 1. Classe: ControleExperimentos -- Classe que define os parametros, executa e mostra o resultado de cada iteração;
// 2. Classe: ResolucaoTarefas -- Será chamada pela classe ControleExperimentos para resolver um instânica de resolução;
// 3. Classe: Maquina - Possui uma pilha de int representando as tarefas e a soma de tempo das tarefas para evitar contagem a cada verificação;