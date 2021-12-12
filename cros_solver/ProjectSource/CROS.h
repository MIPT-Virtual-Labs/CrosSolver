//
// Created by Mitroshin on 08.04.2020.
//

#pragma once
#include <iostream>
#include <complex>
#include <vector>
#include <fstream>
#include <string>
#include <float.h>
#include <algorithm>
#include <iomanip>
using namespace std;

class CROS /* основной класс алгоритма, содержащий все методы и начальные данные*/{ 
  public:
    CROS(unsigned int _N            /* количество переменных*/,
        unsigned int _stepsAmount   /* количество шагов работы алгоритма*/,
        double _T                   /* Длина временного промежутка для рассчётов*/,
        vector<double> _y           /* вектор начальных значений переменных */ );    /*   для запуска алгоритма так же необходим
                                                                                     столбец правых частей funk_ и матрица якоби J_,
                                                                                     которые записаны в генерируемом Jmatrix.h    */
    void RunAlgorithm(const string fileName = "OUT.txt" /* наименование выходного файла*/,
        const int rowsToFile = 1            /*  в выходной файл записывается каждый rowsToFile промежуточный результат*/,
        const bool showProgress = false     /* показывать процент выполнения*/); // запуск алгоритма
    void RunAdaptiveAlgorithm(const string fileName = "OUT.txt", const int rowsToFile = 1, const bool showProgress = true); // экспениментальный алгоритм с адаптивным шагом
    /* == FUNCTIONS FROM Jmatrix.h == */

    vector<vector<double>> (*J_)(vector<double> &y);    // матрица Якоби
    vector<double> (*funk_)(vector<double> &y);         // столбец правых частей

  private:

    /* == INNER ALGORITHMS == */

    void GaussAlgorithm(); // алгоритм Гаусса для первоначального нахождения обратной матрицы J3_. Используется для нахождения начального  приближения
    vector<complex<double>> ShultsAlgorithm(vector<vector<complex<double>>> &approxMatrix); /* алгоритм Шульца (одна итерация первого порядка) для быстрого приближённого 
                                                                                            наждения обратной матрицы. approxMatrix на входе функции - приближение 
                                                                                            обратной матрицы с предыдущего шага, после выполнения функции заменяется на актуальное значение. 
                                                                                            Возвращаемое значение функции - вектор w (g_ в коде) в методе Розенброка */
    void MatrixApproximation(vector<vector<complex<double>>> &init);  /* алгоритм Шульца (одна итерация первого порядка) для быстрого приближённого 
                                                                         наждения обратной матрицы. approxMatrix на входе функции - приближение 
                                                                         обратной матрицы с предыдущего шага, после выполнения функции заменяется на актуальное значение.*/
    unsigned int FindGoodStep(vector<vector<complex<double>>>& matrix, vector<vector<double>>& meanings, double criticalShift = 100.0, unsigned int iterationsAmount = 15); /* функция проверки системы на расхождения в первые   iterationsAmount шагов. 
                                                                                                                                                                            В случае расхождения изменяет шаг до  тех пор , пока расхождение не прекратится */

    void ParametersInitialization();                // обновление численных значений матрицы Якоби, вектора правых частей и промежуточных переменных
    void SaveAnswer();                              // обновление  вектора значений переменных на шаге
    void SetJacobianAndF(vector<double> &y);        // обновление численных значений матрицы Якоби, вектора правых частей
    void SetElements();                             // установка наименований переменных

    /* == FAST PARALLEL WORK WITH VECTORS == */

    vector<vector<double>> InversionMatrix(vector<vector<double>> A, unsigned int N); // обращение матрици методом Гаусса. Используется для нахождения начального  приближения
    vector<vector<double>> TripleMultiplication(vector<vector<double>>& a, vector<vector<double>>& b); /* Умножение матриц по типу A*B*A. 
                                                                                                       Основная параллелизация достигается как раз здесь 
                                                                                                       засчёт распараллеливания умножения матриц  */
    vector<vector<double>> MulMatrixDouble(vector<vector<double>> &a, double b);
    vector<vector<double>> MinusMatrixMatrix(vector<vector<double>> &a, vector<vector<double>> &b); // A-B
    vector<double> MulMatrixVector(vector<vector<double>> &a, vector<double> &b); // A*b
    double MatrixNorm(vector<vector<double>> &arr, string type = "l1");
    double VectorNorm(vector<double> &arr, string type = "l1");
    double MaxShift(vector<double> &norms, int firstNum = 0);
    bool IsCorrectMatrix(vector<vector<double>> &matrix);

    vector<vector<complex<double>>> InversionMatrix(vector<vector<complex<double>>> A, unsigned int N); // обращение матрици методом Гаусса. Используется для нахождения начального  приближения
    vector<vector<complex<double>>> TripleMultiplication(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b); /* Умножение матриц по типу A*B*A. 
                                                                                                                                    Основная параллелизация достигается как раз здесь 
                                                                                                                                    засчёт распараллеливания умножения матриц  */
    vector<vector<complex<double>>> MulMatrixDouble(vector<vector<complex<double>>>& a, double b);
    vector<vector<complex<double>>> MulMatrixComplex(vector<vector<double>>& a, complex<double> b);
    vector<vector<complex<double>>> MinusMatrixMatrix(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b);
    vector<complex<double>> MulMatrixVector(vector<vector<complex<double>>>& a, vector<complex<double>>& b);
    double MatrixNorm(vector<vector<complex<double>>>& arr, string type = "l1"); 
    bool IsCorrectMatrix(vector<vector<complex<double>>>& matrix);
    /* == CONSTANTS == */

    const unsigned int N_; // Количество переменных
   
    const double T_;  // Длина временного промежутка для рассчётов

    /* == OTHER VARIABLES == */

    unsigned int stepsAmount_;  // количество шагов работы алгоритма
    double h_;                  // размер шага по времени
    double halfH_;              // размер половины шага 

    /* == VECTORS == */

    vector<vector<double>> Jacob_;          // текущее численное значение матрицы Якоби
    vector<vector<double>> J1_;             // J1 = E-1/2*hJ - вещественная часть
    vector<vector<double>> J2_;             // J2 = -1/2*hJ - мнимая часть
    vector<vector<complex<double>>> J3_;    // J3 = E-(1+i)/2*hJ - вспомогательный массив для решения системы уравнений с комплексными числами

    vector<double> f_;              // Вектор численных значений правых частей на шаге
    vector<complex<double>> g_;     // Вектор w в методе Розенброка (из решения уравнения J3_ * w = f_)
    vector<double> u_;              // Вектор вещественной части g_
    vector<complex<double>> z_;     // Вспомогательный вектор

    vector<double> y_;              // Вектор значений переменных на шаге (выводится в файл)

    vector<string> elements;        //  массив названий переменных
};

