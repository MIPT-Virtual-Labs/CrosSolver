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

class CROS {
  public:
    CROS(unsigned int _N, unsigned int _stepsAmount, double _T, vector<double> _y);
    void RunAlgorithm(const string fileName = "OUT.txt", const int rowsToFile = 1, const bool showProgress = true);
    void RunAdaptiveAlgorithm(const string fileName = "OUT.txt", const int rowsToFile = 1, const bool showProgress = true);
    /* == FUNCTIONS FROM Jmatrix.h == */

    vector<vector<double>> (*J_)(vector<double> &y);
    vector<double> (*funk_)(vector<double> &y);

  private:

    /* == INNER ALGORITHMS == */

    void GaussAlgorithm();
    vector<complex<double>> ShultsAlgorithm(vector<vector<complex<double>>> &approxMatrix);
    void MatrixApproximation(vector<vector<complex<double>>> &init);
    unsigned int FindGoodStep(vector<vector<complex<double>>>& matrix, vector<vector<double>>& meanings, double criticalShift = 100.0, unsigned int iterationsAmount = 15);

    void ParametersInitialization();
    void SaveAnswer();
    void SetJacobianAndF(vector<double> &y);
    void SetElements();

    /* == FAST PARALLEL WORK WITH VECTORS == */

    vector<vector<double>> InversionMatrix(vector<vector<double>> A, unsigned int N);
    vector<vector<double>> TripleMultiplication(vector<vector<double>>& a, vector<vector<double>>& b);
    vector<vector<double>> MulMatrixDouble(vector<vector<double>> &a, double b);
    vector<vector<double>> MinusMatrixMatrix(vector<vector<double>> &a, vector<vector<double>> &b);
    vector<double> MulMatrixVector(vector<vector<double>> &a, vector<double> &b);
    double MatrixNorm(vector<vector<double>> &arr, string type = "l1");
    double VectorNorm(vector<double> &arr, string type = "l1");
    double MaxShift(vector<double> &norms, int firstNum = 0);
    bool IsCorrectMatrix(vector<vector<double>> &matrix);

    vector<vector<complex<double>>> InversionMatrix(vector<vector<complex<double>>> A, unsigned int N);
    vector<vector<complex<double>>> TripleMultiplication(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b);
    vector<vector<complex<double>>> MulMatrixDouble(vector<vector<complex<double>>>& a, double b);
    vector<vector<complex<double>>> MulMatrixComplex(vector<vector<double>>& a, complex<double> b);
    vector<vector<complex<double>>> MinusMatrixMatrix(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b);
    vector<complex<double>> MulMatrixVector(vector<vector<complex<double>>>& a, vector<complex<double>>& b);
    double MatrixNorm(vector<vector<complex<double>>>& arr, string type = "l1");
    bool IsCorrectMatrix(vector<vector<complex<double>>>& matrix);
    /* == CONSTANTS == */

    const unsigned int N_; // Количество переменных
   
    const double T_;

    /* == OTHER VARIABLES == */

    unsigned int stepsAmount_;
    double h_; //длина шагов по времени
    double halfH_;

    /* == VECTORS == */

    vector<vector<double>> Jacob_;
    vector<vector<double>> J1_; // J1 = E-1/2hJ - вещественная часть
    vector<vector<double>> J2_; // J2 = -1/2hJ - мнимая часть
    vector<vector<complex<double>>> J3_; // Вспомогательный массив для решения системы уравнений с комплексными числами

    vector<double> f_; // Массив правых частей
    vector<complex<double>> g_; // Вспомогательный массив с нулями для массива правых частей
    vector<double> u_; // Массив вещественной части
    vector<complex<double>> z_; // Вспомогательный массив вещественной части с нулями

    vector<double> y_; // Вектор решений (выводится в файл)

    vector<string> elements;
};

