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
//    cout << "|> Run algorithm " << endl;
//    cout << "|> Use " << worldSize << " processing cores. Write every " << rowsToFile << " lines." << endl;
    //logsStream << "|> Use " << worldSize << " processing cores. Write every " << rowsToFile << " lines." << endl;

    unsigned int start_time =  clock();

    if (type == "experiment") {
        CrosAlgorithm.RunAdaptiveAlgorithm(fileName, rowsToFile);
    } else {
        CrosAlgorithm.RunAlgorithm(fileName, rowsToFile);
    }

    unsigned int end_time = clock();

    //cout << endl << "|> DONE!" << endl;
    unsigned int totalTime = (end_time - start_time) / 1000;
//    cout << endl
//    << "|> TOTAL TIME: " << totalTime / 60 << " min "
//    << totalTime % 60 << " sec "
//    << (end_time - start_time) % 1000 << " ms "
//    << endl << endl;

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

    string fileName = "OUT.txt";
    string logsFile = "Logs.txt";

    const int worldSize = omp_get_num_procs(); // получение количества доступных вычислительных ядер
    // cout << "|> Total amount of processing cores " << worldSize << endl;

    ofstream logsStream; // создаем объект класса ifstream
    logsStream.open(logsFile); // открываем файл

    //TestsCROS(worldSize, fileName, logsStream);

    CROS CrosAlgorithm(N, stepsAmount, T, yy);

    const int maxNumProc = static_cast<int>(N / worldSize * 3.5);
    const int optimalNumProc = min(worldSize, maxNumProc);

    RunCROS(CrosAlgorithm, optimalNumProc, 1, fileName, logsStream, "usual");


    // cout << "You can find results in file \"" << fileName << "\" and logs in file \"" << logsFile << "\"." << endl;
    return 0;
}

// Запуск программы: CTRL+F5 или меню "Отладка" > "Запуск без отладки"
// Отладка программы: F5 или меню "Отладка" > "Запустить отладку"

// Советы по началу работы
//   1. В окне обозревателя решений можно добавлять файлы и управлять ими.
//   2. В окне Team Explorer можно подключиться к системе управления версиями.
//   3. В окне "Выходные данные" можно просматривать выходные данные сборки и другие сообщения.
//   4. В окне "Список ошибок" можно просматривать ошибки.
//   5. Последовательно выберите пункты меню "Проект" > "Добавить новый элемент", чтобы создать файлы кода, или "Проект" > "Добавить существующий элемент", чтобы добавить в проект существующие файлы кода.
//   6. Чтобы снова открыть этот проект позже, выберите пункты меню "Файл" > "Открыть" > "Проект" и выберите SLN-файл.
