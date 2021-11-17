//
// Created by Mitroshin on 08.04.2020.
//

#include "CROS.h"

using namespace std;

CROS::CROS(unsigned int _N, unsigned int _stepsAmount, double _T, vector<double> _y):
        N_(_N),
        T_(_T),
        stepsAmount_(_stepsAmount),
        h_(_T / _stepsAmount), //Количество шагов по времени
        halfH_(_T / _stepsAmount / 2),
        
        Jacob_(_N, vector<double>(_N, 0.0)),
        J1_(_N, vector<double>(_N, 0.0)),
        J2_(_N, vector<double>(_N, 0.0)),
        J3_(_N, vector<complex<double>>(_N, 0.0)),
        g_(_N),
        z_(_N),
        f_(_N),
        u_(_N),
        y_(_y)
        {}


void CROS::RunAlgorithm(const string fileName, const int rowsToFile, const bool showProgress) {

    ofstream resultsStream; // создаем объект класса ifstream
    resultsStream.open(fileName); // открываем файл

    ofstream progressStream; // for python progress
    progressStream.open("progress.txt", ios_base::out | ios_base::app);

    double t = 0.0;
    vector<vector<complex<double>>> B;

    unsigned int progress = 0;
    unsigned int currentProgress = 0;

    vector<double> initY = y_;

    const unsigned int iterationsForChecking = 15;
    vector<vector<double>> meanings(iterationsForChecking, vector<double>(N_, 0.0));

    stepsAmount_ = FindGoodStep(B, meanings, 100.0, iterationsForChecking);
    if (stepsAmount_ == 0) {
        progressStream << "failed$"
            << 40
            << "$Количества шагов недостаточно для рассчетов: попробуйте уменьшить параметр времени и пересмотреть зависимости в уравнениях на предмет ошибок$"
            << 0
            << "$0$0\n";
        progressStream.close();
//        cerr << "This program can't find good amount of steps." << endl;
        exit(2);
    } else if (showProgress){
        cout << "Program has " << stepsAmount_ << " steps." << endl;
    }

    h_ = T_ / stepsAmount_;
    halfH_ = h_ / 2;

    // First step of the algorithm
//    ParametersInitialization();
//    B = InversionMatrix(J3_, J3_.size());
//    GaussAlgorithm();
//    SaveAnswer();
//    t += h_;
//
//    for (int k = 0; k < N_; ++k) {
//        resultsStream << y_[k] << "  ";
//    }
//    resultsStream << endl;

    for (int j = 1; j <= iterationsForChecking; ++j) {
        if (showProgress) {
            currentProgress = static_cast<unsigned int>(j * 100 / stepsAmount_);
            if (currentProgress != progress) {
                cout << "\rCompleted " << currentProgress << "%     " << flush;
                progress = currentProgress;
            }
        }
        if (j % rowsToFile == 0) {
            for (int k = 0; k < N_; ++k) {
                resultsStream << meanings[j-1][k] << "\t";
            }
            resultsStream << endl;
        }
    }

    // int i = iterationsForChecking + 1;
    t = h_ * iterationsForChecking;

    for (int i = iterationsForChecking + 1; i <= stepsAmount_; i++) {
        ParametersInitialization();
        g_ = ShultsAlgorithm(B);
        SaveAnswer();
        t += h_;

        currentProgress = static_cast<unsigned int>(i * 100 / stepsAmount_);
        if (showProgress) {
            if (currentProgress != progress) {
                cout << "\rCompleted " << currentProgress << "%     " << flush;
                //progress = currentProgress;
            }
        }
        if (currentProgress != progress && currentProgress < 100) {
            progressStream << "process$"
            << static_cast<unsigned int>(40 + 0.6 * currentProgress)
            << "$Run program$"
            << currentProgress
            << "$0$0\n";
            progress = currentProgress;
        }
        if (i % rowsToFile == 0) {
            for (int k = 0; k < N_; ++k) {
                resultsStream << y_[k] << "\t";
            }
            resultsStream << endl;
        }
        for (int q = 0; q < 5000000; q++) {}
    }

    resultsStream.close();

    progressStream << "process$"
            << 100
            << "$Run program$"
            << 100
            << "$0$0\n";
    progressStream.close();
}


void CROS::RunAdaptiveAlgorithm(const string fileName, const int rowsToFile, const bool showProgress) {

    ofstream resultsStream; // создаем объект класса ifstream
    resultsStream.open(fileName); // открываем файл

    double t = 0.0;
    vector<vector<complex<double>>> B;
    cout.setf(ios::fixed);

    unsigned int progress = 0;
    unsigned int currentProgress = 0;

    vector<double> initY = y_;

    const unsigned int iterationsForChecking = 15;
    vector<vector<double>> meanings(iterationsForChecking, vector<double>(N_, 0.0));

    stepsAmount_ = FindGoodStep(B, meanings, 100.0, iterationsForChecking);
    if (stepsAmount_ == 0) {
        cerr << "This program can't find good amount of steps." << endl;
        exit(2);
    } else if (showProgress){
        cout << "Program has " << stepsAmount_ << " steps." << endl;
    }

    h_ = T_ / stepsAmount_;
    halfH_ = h_ / 2;

    // First step of the algorithm
//    ParametersInitialization();
//    B = InversionMatrix(J3_, J3_.size());
//    GaussAlgorithm();
//    SaveAnswer();
//    t += h_;
//
//    for (int k = 0; k < N_; ++k) {
//        resultsStream << y_[k] << "  ";
//    }
//    resultsStream << endl;

    //t = h_ * iterationsForChecking;

    for (int j = 1; j <= iterationsForChecking; ++j) {
        t += h_;
        if (showProgress) {
            currentProgress = static_cast<unsigned int>(t * 100 / T_);
            if (currentProgress != progress) {
                int localCoef = h_ < 10.0 ? 0 : (h_ < 100.0 ? 1 : (h_ < 1000.0 ? 2 : 3));
                cout << "\rStep = " << setprecision (8 - localCoef) << h_ << " | Completed " << currentProgress << "%     " << flush;
                progress = currentProgress;
            }
        }
        if (j % rowsToFile == 0) {
            resultsStream << "t=" << t << " | h_=" << h_ << " | ";
            for (int k = 0; k < N_; ++k) {
                resultsStream << meanings[j - 1][k] << "  ";
            }
            resultsStream << endl;
        }
    }

    int i = iterationsForChecking + 1;

    vector<vector<complex<double>>> prevStepMatrix = B;
    vector<double> prevY = y_;
    double coefOfIncreasing = 1.2;
    int stepsWithoutChangeH = 16;
    double criticalMatrixNorm = N_ * 0.35;
    const double criticalCoefVectorNorm = 1.25;

    while (t < T_) {
        ParametersInitialization();
        g_ = ShultsAlgorithm(B);
        SaveAnswer();
        t += h_;

        if (showProgress) {
            currentProgress = static_cast<unsigned int>(t * 100 / T_);
            if (currentProgress != progress) {
                int localCoef = h_ < 10.0 ? 0 : (h_ < 100.0 ? 1 : (h_ < 1000.0 ? 2 : 3));
                cout << "\rStep = " << setprecision (8 - localCoef) << h_ << " | Completed " << currentProgress << "%     " << flush;
                progress = currentProgress;
            }
        }
        if (i % rowsToFile == 0 || t >= T_) {
            resultsStream << "t=" << t << " | h_=" << h_ << " | ";
            for (int k = 0; k < N_; ++k) {
                resultsStream << y_[k] << "  ";
            }
            resultsStream << endl;
        }

        if (i % stepsWithoutChangeH == 0 && t < T_) {
            vector<vector<complex<double>>> differenceMatrix = MinusMatrixMatrix(prevStepMatrix, B);
            double newNorm = MatrixNorm(differenceMatrix);
            prevStepMatrix = B;

            double vectorNorm = VectorNorm(prevY);
            double vectorNorm2 = VectorNorm(y_);
            double maxCoeffVector = max(vectorNorm / vectorNorm2, vectorNorm2 / vectorNorm);
            prevY = y_;


            //cout << "Matrix norm: "<< newNorm << " | Vector diff norm: " << maxCoeffVector << " | h_ = " << h_ << endl;

            if (newNorm <= criticalMatrixNorm && maxCoeffVector <= criticalCoefVectorNorm) {
                h_ *= coefOfIncreasing;
                halfH_ = h_ / 2;
                initY = y_;

                // Step of the algorithm
                ParametersInitialization();
                g_ = ShultsAlgorithm(B);
                SaveAnswer();

                differenceMatrix = MinusMatrixMatrix(prevStepMatrix, B);
                double newNorm2 = MatrixNorm(differenceMatrix);


                double vectorNorm3 = VectorNorm(y_);
                maxCoeffVector = max(vectorNorm3 / vectorNorm2, vectorNorm2 / vectorNorm3);

                //cout << "Matrix norm: "<< newNorm2 << " | Vector norm: " << maxCoeffVector << endl;
                if (newNorm2 <= criticalMatrixNorm && maxCoeffVector <= criticalCoefVectorNorm) {
                    //cout << "Update step!!! New h_ = " << h_ << endl;
                    t += h_;
//                    if (stepsWithoutChangeH >= 8) {
//                        stepsWithoutChangeH = static_cast<int>(1.5 * stepsWithoutChangeH);
//                    }
                    if (i % rowsToFile == 0 || t >= T_) {
                        resultsStream << "t=" << t << " | h_=" << h_ << " | ";
                        for (int k = 0; k < N_; ++k) {
                            resultsStream << y_[k] << "  ";
                        }
                        resultsStream << endl;
                    }
                    coefOfIncreasing *= 1.1;
                } else {
                    //stepsWithoutChangeH  *= 2;
                    B = prevStepMatrix;
                    y_ = initY;
                    h_ /= coefOfIncreasing;
                    halfH_ = h_ / 2;
                    if (coefOfIncreasing / 1.09 >= 1.01) {
                        coefOfIncreasing /= 1.09;
                    }
                }
            }
        }

        ++i;
    }

    resultsStream.close();
}


unsigned int CROS::FindGoodStep(vector<vector<complex<double>>>& matrix, vector<vector<double>>& meanings, double criticalShift, unsigned int iterationsAmount) {
	vector<double> norms(iterationsAmount, 0.0);
	vector<double> initY = y_;
	unsigned int currentAns = 0;
	unsigned int totalChanges = 0;
	while (true) {

		y_ = initY;
		h_ = T_ / stepsAmount_;
		halfH_ = h_ / 2;

		// First step of the algorithm
		ParametersInitialization();
//		for (int qq = 0; qq < J1_.size(); ++qq) {
//			cout << qq << "| ";
//			for (int qq2 = 0; qq2 < J1_.size(); ++qq2) {
//				cout << J1_[qq][qq2] << " ";
//			}
//			cout << endl;
//		}

		matrix = InversionMatrix(J3_, J3_.size());
		//        for (int qq = 0; qq < matrix.size(); ++qq) {
		//            cout << qq << "| ";
		//            for (int qq2 = 0; qq2 < matrix.size(); ++qq2) {
		//                cout << matrix[qq][qq2] << " ";
		//            }
		//            cout << endl;
		//        }
		//        sleep(3);
				//if (!IsCorrectMatrix(matrix)) {}
		GaussAlgorithm();
		SaveAnswer();
		meanings[0] = y_;
		norms[0] = MatrixNorm(matrix);


		totalChanges += 1;
		if (totalChanges >= 76) {
			return 0;
		}
		bool badMatrix = false;
		for (int i = 1; i < iterationsAmount; ++i) {
			ParametersInitialization();
			g_ = ShultsAlgorithm(matrix);
			SaveAnswer();
			meanings[i] = y_;
			//            for (int qq = 0; qq < matrix.size(); ++qq) {
			//                cout << qq << "| ";
			//                for (int qq2 = 0; qq2 < matrix.size(); ++qq2) {
			//                    cout << matrix[qq][qq2] << " ";
			//                }
			//                cout << endl;
			//            }
			//            sleep(3);
			norms[i] = MatrixNorm(matrix);
			if (!IsCorrectMatrix(matrix)) {
				badMatrix = true;
				cout << "BAD MATRIX NORM = " << norms[i] << endl;
				//                for (int qq = 0; qq < matrix.size(); ++qq) {
				//                    cout << qq << "| ";
				//                    for (int qq2 = 0; qq2 < matrix.size(); ++qq2) {
				//                        cout << matrix[qq][qq2] << " ";
				//                    }
				//                    cout << endl;
				//                }
				//                sleep(3);
				break;
			}
		}
		if (badMatrix) {
			// ATTENTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			// ДИКИЙ КОСТЫЛЬ - СЛЕДУЩИЕ 3 СТРОКИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//            cout << "Не нашёл я нужного шага, поэтому давай так, но с проверочкой)))))" << endl;
//            currentAns = stepsAmount_;
//            return currentAns;
			// END OF КОСТЫЛЬ
			cout << "Bad matrix" << " | Steps amount = " << stepsAmount_ << " | Finding another step..." << endl;
			stepsAmount_ = static_cast<unsigned int>(stepsAmount_ * 1.2);
			continue;
		}
		double shift = MaxShift(norms);
		//cout << "Shift = " << shift << " | Steps amount = " << stepsAmount_ << endl;

		if (shift <= criticalShift) {
			currentAns = stepsAmount_;
			return currentAns;
		}

		cout << "Bag shift = " << shift << " | Steps amount = " << stepsAmount_ << " | Finding another step..." << endl;

		stepsAmount_ = static_cast<unsigned int>(stepsAmount_ * 1.2);
	}
}

bool CROS::IsCorrectMatrix(vector<vector<double>> &matrix) {
    for (int i = 0; i < matrix.size(); ++i) {
        for (int j = 0; j < matrix.size(); ++j) {
            if (matrix[i][j] != matrix[i][j] ||
                    !(matrix[i][j] <= DBL_MAX && matrix[i][j] >= -DBL_MAX)) {
                return false;
            }
        }
    }
    return true;
}
bool CROS::IsCorrectMatrix(vector<vector<complex<double>>>& matrix) {
	for (int i = 0; i < matrix.size(); ++i) {
		for (int j = 0; j < matrix.size(); ++j) {
			if (matrix[i][j] != matrix[i][j] ||
				!(abs(matrix[i][j]) <= DBL_MAX && abs(matrix[i][j]) >= -DBL_MAX)) {
				return false;
			}
		}
	}
	return true;
}

double CROS::MaxShift(vector<double> &norms, int firstNum) {
    double maxDifference = 0.0;
    double currentDifference = 0.0;
    for (int i = firstNum; i < norms.size() - 1; i++) {
        currentDifference = norms[i + 1] / norms[i];
        if (currentDifference > maxDifference) {
            maxDifference = currentDifference;
        }
    }
    return maxDifference;
}

double CROS::MatrixNorm(vector<vector<double>> &arr, string type) {
    unsigned int size = arr.size();
    double ans = 0.0;
    if (type == "l1") {

        #pragma omp parallel for
        for (int i = 0; i <size; i++) {
            for (int j = 0; j < size; j++) {
                ans += abs(arr[i][j]);
            }
        }

    } else if (type == "l2") {

        #pragma omp parallel for
        for (int i = 0; i <size; i++) {
            for (int j = 0; j < size; j++) {
                ans += arr[i][j] * arr[i][j];
            }
        }
        ans = sqrt(ans);

    } else { // default l1

        #pragma omp parallel for
        for (int i = 0; i <size; i++) {
            for (int j = 0; j < size; j++) {
                ans += abs(arr[i][j]);
            }
        }

    }
    return ans;
}
double CROS::MatrixNorm(vector<vector<complex<double>>>& arr, string type) {
	unsigned int size = arr.size();
	double ans = 0.0;
	if (type == "l1") {

#pragma omp parallel for
		for (int i = 0; i < size; i++) {
			for (int j = 0; j < size; j++) {
				ans += abs(arr[i][j]);
			}
		}

	}
	else if (type == "l2") {

#pragma omp parallel for
		for (int i = 0; i < size; i++) {
			for (int j = 0; j < size; j++) {
				ans += abs(arr[i][j] * arr[i][j]);
			}
		}
		ans = sqrt(ans);

	}
	else { // default l1

#pragma omp parallel for
		for (int i = 0; i < size; i++) {
			for (int j = 0; j < size; j++) {
				ans += abs(arr[i][j]);
			}
		}

	}
	return ans;
}
double CROS::VectorNorm(vector<double> &arr, string type) {
    unsigned int size = arr.size();
    double ans = 0.0;
    if (type == "l1") {
        for (int i = 0; i <size; i++) {
            ans += abs(arr[i]);
        }
    } else if (type == "l2") {
        for (int i = 0; i <size; i++) {
            ans += arr[i] * arr[i];
        }
        ans = sqrt(ans);

    } else { // default l1
        for (int i = 0; i <size; i++) {
            ans += abs(arr[i]);
        }
    }
    return ans;
}

void CROS::SaveAnswer() {
	
	z_= g_;
	
    

    for (int j = 0; j < N_; j++) {
        u_[j] = z_[j].real();
    }

    for (int j = 0; j < N_; j++) {
        y_[j] = y_[j] + h_ * u_[j];
    }
}

void CROS::ParametersInitialization() {
    SetJacobianAndF(y_);
//    Jacob_ = J_(y_);       //Подсчёт текущего значения J
//    f_ = funk_(y_);

    J1_ = MulMatrixDouble(Jacob_, -halfH_); //Подсчёт текущего значения J1
    J3_ = MulMatrixComplex(J1_, (1.0 + 1i) / 2.0);

    for (int j = 0; j < N_; j++) {
        J3_[j][j] += 1.0;
    }



    for (int j = 0; j < N_; j++) {					//Столбец вспомогательных функций правой части
        g_[j] = f_[j];
    }
}

vector<complex<double>> CROS::ShultsAlgorithm(vector<vector<complex<double>>> &approxMatrix) {
        MatrixApproximation(approxMatrix);
        return MulMatrixVector(approxMatrix, g_);
};

void CROS::MatrixApproximation(vector<vector<complex<double>>> &init) {
    vector<vector<complex<double>>> tmp = MulMatrixDouble(init, 2.0);
    vector<vector<complex<double>>> tmp2 = TripleMultiplication(init, J3_);
    init = MinusMatrixMatrix(tmp, tmp2);
};

void CROS::GaussAlgorithm(){
	complex<double> R,  cc;                 //Вспомогательное число для метода Гаусса
    vector<complex<double>> c(N_);

    for (int k = 0; k < N_; k++) {    //Метод Гаусса
        double max;
        int ind_max;

        max = abs(J3_[k][k]);
        ind_max = k;

        for (int j = k + 1; j < N_; j++) {
            if (abs(J3_[j][k]) > max) {
                ind_max = j;
            }
        }

        for (int j = 0; j < N_; j++) {
            c[j] = J3_[k][j];
            J3_[k][j] = J3_[ind_max][j];
            J3_[ind_max][j] = c[j];
        }

        cc = g_[k];
        g_[k] = g_[ind_max];
        g_[ind_max] = cc;

        for (int j = 0; j < N_; j++) {
            if (j != k) {
                if (J3_[j][k] != 0.0) {
                    R = J3_[k][k] / J3_[j][k];

                    for (int l = 0; l < N_; l++) {
                        J3_[j][l] = J3_[j][l] - J3_[k][l] / R;
                    }
                    g_[j] = g_[j] - g_[k] / R;
                }
            }
        }

        for (int j = 0; j < N_; j++)
            if (j != k)
                J3_[k][j] = J3_[k][j] / J3_[k][k];
        g_[k] = g_[k] / J3_[k][k];
        J3_[k][k] = 1;
    }
}

vector<vector<double>> CROS::InversionMatrix(vector<vector<double>> A, unsigned int N){
    double temp;

    vector<vector<double>> E(N, vector<double>(N, 0.0));

    for (int i = 0; i < N; i++)
        E[i][i] = 1.0;


    for (int k = 0; k < N; k++) {
        temp = A[k][k];
        for (int j = 0; j < N; j++) {
            A[k][j] /= temp;
            E[k][j] /= temp;
        }

        for (int i = k + 1; i < N; i++) {
            temp = A[i][k];

            for (int j = 0; j < N; j++) {
                A[i][j] -= A[k][j] * temp;
                E[i][j] -= E[k][j] * temp;
            }
        }
    }

    for (int k = N - 1; k > 0; k--) {
        for (int i = k - 1; i >= 0; i--) {
            temp = A[i][k];
            for (int j = 0; j < N; j++) {
                A[i][j] -= A[k][j] * temp;
                E[i][j] -= E[k][j] * temp;
            }
        }
    }

    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            A[i][j] = E[i][j];

    return A;
}

vector<vector<complex<double>>> CROS::InversionMatrix(vector<vector<complex<double>>> A, unsigned int N) {
	complex<double> temp;

	vector<vector<complex<double>>> E(N, vector<complex<double>>(N, 0.0));

	for (int i = 0; i < N; i++)
		E[i][i] = 1.0;


	for (int k = 0; k < N; k++) {
		temp = A[k][k];
		for (int j = 0; j < N; j++) {
			A[k][j] /= temp;
			E[k][j] /= temp;
		}

		for (int i = k + 1; i < N; i++) {
			temp = A[i][k];

			for (int j = 0; j < N; j++) {
				A[i][j] -= A[k][j] * temp;
				E[i][j] -= E[k][j] * temp;
			}
		}
	}

	for (int k = N - 1; k > 0; k--) {
		for (int i = k - 1; i >= 0; i--) {
			temp = A[i][k];
			for (int j = 0; j < N; j++) {
				A[i][j] -= A[k][j] * temp;
				E[i][j] -= E[k][j] * temp;
			}
		}
	}

	for (int i = 0; i < N; i++)
		for (int j = 0; j < N; j++)
			A[i][j] = E[i][j];

	return A;
}
vector<vector<double>> CROS::TripleMultiplication(vector<vector<double>>& a, vector<vector<double>>& b) {
    unsigned int size = a.size();
    vector<vector<double>> tmp(size, vector<double>(size, 0.0));
    vector<vector<double>> tmp2(size, vector<double>(size, 0.0));

    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        for (int k = 0; k < size; k++) {
            for (int t = 0; t < size; t++) {
                tmp[i][k] += a[i][t] * b[t][k];
            }
        }
    }

    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        for (int k = 0; k < size; k++) {
            for (int t = 0; t < size; t++) {
                tmp2[i][k] += tmp[i][t] * a[t][k]; // c == a
            }
        }
    }
    return tmp2;
}
vector<vector<complex<double>>> CROS::TripleMultiplication(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b) {
	unsigned int size = a.size();
	vector<vector<complex<double>>> tmp(size, vector<complex<double>>(size, 0.0));
	vector<vector<complex<double>>> tmp2(size, vector<complex<double>>(size, 0.0));

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			for (int t = 0; t < size; t++) {
				tmp[i][k] += a[i][t] * b[t][k];
			}
		}
	}

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			for (int t = 0; t < size; t++) {
				tmp2[i][k] += tmp[i][t] * a[t][k]; // c == a
			}
		}
	}
	return tmp2;
}

vector<vector<double>> CROS::MulMatrixDouble(vector<vector<double>> &a, double b) {
    unsigned int size = a.size();
    vector<vector<double>> tmp(size, vector<double>(size, 0.0));

    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        for (int k = 0; k < size; k++) {
            tmp[i][k] = a[i][k] * b;
        }
    }

    return tmp;
}
vector<vector<complex<double>>> CROS::MulMatrixDouble(vector<vector<complex<double>>>& a, double b) {
	unsigned int size = a.size();
	vector<vector<complex<double>>> tmp(size, vector<complex<double>>(size, 0.0));

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			tmp[i][k] = a[i][k] * b;
		}
	}

	return tmp;
}
vector<vector<complex<double>>> CROS::MulMatrixComplex(vector<vector<double>>& a, complex<double> b) {
	unsigned int size = a.size();
	vector<vector<complex<double>>> tmp(size, vector<complex<double>>(size, 0.0));

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			tmp[i][k] = a[i][k] * b;
		}
	}

	return tmp;
}
vector<vector<double>> CROS::MinusMatrixMatrix(vector<vector<double>> &a, vector<vector<double>> &b) {
    unsigned int size = a.size();
    vector<vector<double>> tmp(size, vector<double>(size, 0.0));

    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        for (int k = 0; k < size; k++) {
            tmp[i][k] = a[i][k] - b[i][k];
        }
    }
    return tmp;
}
vector<vector<complex<double>>> CROS::MinusMatrixMatrix(vector<vector<complex<double>>>& a, vector<vector<complex<double>>>& b) {
	unsigned int size = a.size();
	vector<vector<complex<double>>> tmp(size, vector<complex<double>>(size, 0.0));

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			tmp[i][k] = a[i][k] - b[i][k];
		}
	}
	return tmp;
}
vector<double> CROS::MulMatrixVector(vector<vector<double>> &a, vector<double> &b) {
    unsigned int size = a.size();
    vector<double> tmp(size, 0);

    #pragma omp parallel for
    for (int i = 0; i < size; i++) {
        for (int k = 0; k < size; k++) {
            tmp[i] += a[i][k] * b[k];
        }
    }

    return tmp;
};
vector<complex<double>> CROS::MulMatrixVector(vector<vector<complex<double>>>& a, vector<complex<double>>& b) {
	unsigned int size = a.size();
	vector<complex<double>> tmp(size, 0);

#pragma omp parallel for
	for (int i = 0; i < size; i++) {
		for (int k = 0; k < size; k++) {
			tmp[i] += a[i][k] * b[k];
		}
	}

	return tmp;
};