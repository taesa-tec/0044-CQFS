# 2     ORGANIZAÇÃO CONCEITUAL DOS MODELOS E DEFINIÇÃO DO ARRANJO DO PLUGIN

Para se determinar o arranjo de sistematização dos modelos e criação das ferramentas do CQFS, foi estudada a dinâmica de interação entre os modelos criados para o projeto, isto é, se a saída de um modelo é entrada para outro modelo, a frequência de atualização dos dados de entrada, que, consequentemente, leva à necessidade de execução do modelo e atualização dos dados de saída. Com base nesse estudo, definiu-se o arranjo conceitual final das ferramentas do plugin, conforme mostrado na Figura 1.


![Arranjo conceitual para construção do plugin](Figuras_Manual/Figura_1.PNG)
​

Figura 1 – Arranjo conceitual para construção do plugin



Cada modelo é representado por uma ferramenta, que são interconectadas entre si – através das entradas e saídas dos modelos. Entretanto, a execução de uma ferramenta foi definida de forma independente das outras pois isso possibilita ao usuário uma maior liberdade na escolha do modelo que deseja executar, de acordo com a sua necessidade e forma de trabalho.

Para a geração dos dados de Criticidade (resultado final), o usuário poderá escolher iniciar o processo pela ferramenta de Vulnerabilidade ou pelas ferramentas de Ignição e Propagação. Após o usuário ter gerado os dados de Ignição e Propagação ele poderá executar a ferramenta de Risco de Fogo. Tendo os dados de Risco de Fogo e Vulnerabilidade, finalmente o usuário poderá executar a ferramenta de Criticidade e obter os resultados.

Como os dados de entrada das ferramentas possuem frequências de atualização distintas, esse arranjo permite que somente a informação que necessite de atualização no modelo seja processada e atualizada, poupando o tempo do usuário com atualizações de dados desnecessárias.
