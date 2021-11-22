// main.cpp : Этот файл содержит функцию "main". Здесь начинается и заканчивается выполнение программы.

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <ctime>
#include <cmath>
#include "CROS.h"
#include "Jmatrix.h"
using namespace std;


void RunCROS(CROS& CrosAlgorithm, const int worldSize, const int rowsToFile,
        string& fileName, ofstream& logsStream, const string type = "usual") {

    omp_set_num_threads(worldSize);

    unsigned int start_time =  clock();

    if (type == "experiment") {
        CrosAlgorithm.RunAdaptiveAlgorithm(fileName, rowsToFile); //эспериментальная функция адаптивного шага
    } else {
        CrosAlgorithm.RunAlgorithm(fileName, rowsToFile); // Запуск алгоритма CROS
    }

    unsigned int end_time = clock();

    unsigned int totalTime = (end_time - start_time) / 1000;

    logsStream << "| TIME: " << totalTime / 60 << " min "
    << totalTime % 60 << " sec "
    << (end_time - start_time) % 1000 << " ms " << endl;
}

void TestsCROS(const int worldSize, string& fileName, ofstream& logsStream) {
    for (int i = 0; i < worldSize; ++i) {
        logsStream
                << "======================================" << endl
                << "============ " << "|> WS = " << worldSize - i << endl;
        for (int j = 1; j < 8000; j *= 16) {
            logsStream << "====== " << "|> Rows = " << j << endl;
            for (int k = 1; k < 6; ++k) {
                logsStream << "Test " << k << " ";
                CROS CrosAlgorithm(N, stepsAmount, T, yy);

                RunCROS(CrosAlgorithm, worldSize - i, j, fileName, logsStream);
            }
        }
    }
}


int main() {

    //cout << "|> Initialization..." << endl;
    int rowsRarity = 1;                             // В выходной файл записывается каждый rowsRarity промежуточный результат

    string fileName = "OUT.txt";                    // Имя выходного файла 
    string logsFile = "Logs.txt";                   // Имя файла логов

    const int worldSize = omp_get_num_procs();      // получение количества доступных вычислительных ядер

    // cout << "|> Total amount of processing cores " << worldSize << endl;

    ofstream logsStream;                            // создаем объект класса ifstream
    logsStream.open(logsFile);                      // открываем файл

    //TestsCROS(worldSize, fileName, logsStream);

    CROS CrosAlgorithm(N, stepsAmount, T, yy);

    const int maxNumProc = static_cast<int>(N / worldSize * 3.5);       // Экспериментально : после большего числа параллельных потоков производительность падает
    const int optimalNumProc = min(worldSize, maxNumProc);              // выбираем оптимальное кол-во потоков

    RunCROS(CrosAlgorithm, optimalNumProc, rowsRarity, fileName, logsStream, "usual");

    return 0;
}
