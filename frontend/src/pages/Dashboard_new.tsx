/**
 * Dashboard Page
 * 
 * Main dashboard for authenticated users - role-based functionality
 * REQUIREMENTS:
 * - Admin: Create exams only
 * - Supervisor: Assign votes only  
 * - User: View available exams + register for exams + view "my exams"
 */

import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, Button } from '../components/ui';
import { CreateExamModal } from '../components/CreateExamModal';
import { AssignVoteModal } from '../components/AssignVoteModal';
import { apiClient } from '../services/api';
import { Exam, UserExam } from '../types';

export function Dashboard() {
  const { user, logout } = useAuth();
  const [userExams, setUserExams] = useState<UserExam[]>([]);
  const [availableExams, setAvailableExams] = useState<Exam[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modals
  const [showCreateExamModal, setShowCreateExamModal] = useState(false);
  const [showAssignVoteModal, setShowAssignVoteModal] = useState(false);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Always load available exams (public endpoint)
      const publicExamsData = await apiClient.getPublicExams();
      setAvailableExams(Array.isArray(publicExamsData) ? publicExamsData : []);
      
      // Only load user exams if user role
      if (user?.role === 'user') {
        const userExamsData = await apiClient.getUserExams();
        setUserExams(Array.isArray(userExamsData) ? userExamsData : []);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleRegisterForExam = async (examId: number) => {
    try {
      await apiClient.registerForExam(examId);
      await loadData(); // Refresh data
    } catch (err: any) {
      setError(err.message || 'Failed to register for exam');
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Exam Transcripts Dashboard
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.email}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 capitalize">
                {user?.role}
              </span>
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Admin Role: Create Exams Only */}
        {user?.role === 'admin' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Admin Dashboard</h2>
              <Button onClick={() => setShowCreateExamModal(true)}>
                Create New Exam
              </Button>
            </div>
            
            <Card title="Available Exams">
              {availableExams.length === 0 ? (
                <p className="text-gray-500">No exams created yet.</p>
              ) : (
                <div className="space-y-4">
                  {availableExams.map((exam) => (
                    <div key={exam.id} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900">{exam.title}</h4>
                      <p className="text-sm text-gray-500">
                        Date: {new Date(exam.date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Supervisor Role: Assign Votes Only */}
        {user?.role === 'supervisor' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Supervisor Dashboard</h2>
              <Button onClick={() => setShowAssignVoteModal(true)}>
                Assign Vote
              </Button>
            </div>
            
            <Card title="Available Exams">
              {availableExams.length === 0 ? (
                <p className="text-gray-500">No exams available.</p>
              ) : (
                <div className="space-y-4">
                  {availableExams.map((exam) => (
                    <div key={exam.id} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900">{exam.title}</h4>
                      <p className="text-sm text-gray-500">
                        Date: {new Date(exam.date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* User Role: Register for Exams + View My Exams */}
        {user?.role === 'user' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* My Exams */}
            <Card title="My Exams">
              {userExams.length === 0 ? (
                <p className="text-gray-500">No exams registered yet.</p>
              ) : (
                <div className="space-y-4">
                  {userExams.map((userExam) => (
                    <div key={userExam.exam_id} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900">{userExam.exam_title}</h4>
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          Date: {new Date(userExam.exam_date).toLocaleDateString()}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          userExam.is_graded 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {userExam.is_graded ? `Grade: ${userExam.vote}/100` : 'Pending'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Available Exams to Register */}
            <Card title="Available Exams">
              {availableExams.length === 0 ? (
                <p className="text-gray-500">No exams available.</p>
              ) : (
                <div className="space-y-4">
                  {availableExams.map((exam) => {
                    const isRegistered = userExams.some(ue => ue.exam_id === exam.id);
                    return (
                      <div key={exam.id} className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900">{exam.title}</h4>
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-sm text-gray-500">
                            Date: {new Date(exam.date).toLocaleDateString()}
                          </span>
                          <Button
                            size="sm"
                            disabled={isRegistered}
                            onClick={() => handleRegisterForExam(exam.id)}
                          >
                            {isRegistered ? 'Registered' : 'Register'}
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          </div>
        )}
      </main>

      {/* Modals */}
      <CreateExamModal
        isOpen={showCreateExamModal}
        onClose={() => setShowCreateExamModal(false)}
        onSuccess={() => {
          setShowCreateExamModal(false);
          loadData();
        }}
      />
      
      <AssignVoteModal
        isOpen={showAssignVoteModal}
        onClose={() => setShowAssignVoteModal(false)}
        onSuccess={() => {
          setShowAssignVoteModal(false);
          loadData();
        }}
      />
    </div>
  );
}
