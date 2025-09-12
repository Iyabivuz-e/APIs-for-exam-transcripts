/**
 * Dashboard Page
 * 
 * Main dashboard for authenticated users - role-based functionality
 * REQUIREMENTS:
 * - Admin: Create exams only
 * - Supervisor: Assign votes only  
 * - User: View available exams + register for exams + view "my exams"
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, Button } from '../components/ui';
import { CreateExamModal } from '../components/CreateExamModal';
import { AssignVoteToUserModal } from '../components/AssignVoteToUserModal';
import { apiClient } from '../services/api';
import { Exam, UserExam, User } from '../types';

export function Dashboard() {
  const { user, logout } = useAuth();
  const [userExams, setUserExams] = useState<UserExam[]>([]);
  const [availableExams, setAvailableExams] = useState<Exam[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [usersWithExams, setUsersWithExams] = useState<Set<string>>(new Set()); // Changed from number to string for UUID
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Modals
  const [showCreateExamModal, setShowCreateExamModal] = useState(false);
  const [showAssignVoteModal, setShowAssignVoteModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedUserEmail, setSelectedUserEmail] = useState<string>('');

  const checkUsersWithExams = useCallback(async (users: User[]) => {
    try {
      const usersWithExamsSet = new Set<string>(); // Changed from number to string for UUID
      
      // Check each user to see if they have ungraded exams
      await Promise.all(
        users.map(async (userData) => {
          const hasExams = await apiClient.checkUserHasUngradedExams(userData.id);
          if (hasExams) {
            usersWithExamsSet.add(userData.id);
          }
        })
      );
      
      setUsersWithExams(usersWithExamsSet);
    } catch (error) {
      // Silently fail - UI will handle empty state
    }
  }, []);

  const loadData = useCallback(async () => {
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
      
      // Load all users for supervisors to assign votes
      if (user?.role === 'supervisor') {
        const usersData = await apiClient.getUsers();
        setAllUsers(Array.isArray(usersData) ? usersData : []);
        
        // Check which users have ungraded exams
        await checkUsersWithExams(usersData);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, [user?.role, checkUsersWithExams]);

  useEffect(() => {
    loadData();
  }, [user, loadData]);

  const handleRegisterForExam = async (examId: string) => { // Changed from number to string for UUID
    try {
      await apiClient.registerForExam(examId);
      await loadData(); // Refresh data
    } catch (err: any) {
      setError(err.message || 'Failed to register for exam');
    }
  };

  const handleDeleteExam = async (examId: string) => { // Changed from number to string for UUID
    if (!window.confirm('Are you sure you want to delete this exam?')) {
      return;
    }
    
    try {
      await apiClient.deleteExam(examId);
      setSuccessMessage('Exam deleted successfully');
      setTimeout(() => setSuccessMessage(null), 3000); // Clear message after 3 seconds
      await loadData(); // Refresh data
    } catch (err: any) {
      setError(err.message || 'Failed to delete exam');
    }
  };

  const handleAssignVote = (userId: string, userEmail: string) => { // Changed from number to string for UUID
    // Check if user has ungraded exams before opening modal
    if (!usersWithExams.has(userId)) {
      setError('This user has no ungraded exams available for voting');
      setTimeout(() => setError(null), 3000);
      return;
    }
    
    setSelectedUserId(userId);
    setSelectedUserEmail(userEmail);
    setShowAssignVoteModal(true);
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

        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-600">{successMessage}</p>
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
                    <div key={exam.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center">
                      <div>
                        <h4 className="font-medium text-gray-900">{exam.title}</h4>
                        <p className="text-sm text-gray-500">
                          Date: {new Date(exam.date).toLocaleDateString()}
                        </p>
                      </div>
                      <Button 
                        variant="secondary" 
                        size="sm"
                        onClick={() => handleDeleteExam(exam.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Supervisor Role: Assign Votes to Users */}
        {user?.role === 'supervisor' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Supervisor Dashboard</h2>
              <p className="text-sm text-gray-600">Assign votes to users for their exam submissions</p>
            </div>
            
            {/* Users Section */}
            <Card title="Users Available for Vote Assignment">
              {allUsers.length === 0 ? (
                <p className="text-gray-500">No users available for vote assignment.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {allUsers.map((userData) => {
                    const hasExams = usersWithExams.has(userData.id);
                    return (
                      <div key={userData.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{userData.email}</h4>
                            <p className="text-sm text-gray-500 capitalize">Role: {userData.role}</p>
                            {!hasExams && (
                              <p className="text-xs text-orange-600 mt-1">No ungraded exams available</p>
                            )}
                          </div>
                          <Button 
                            size="sm"
                            onClick={() => handleAssignVote(userData.id, userData.email)}
                            disabled={!hasExams}
                            className={hasExams 
                              ? "bg-blue-600 hover:bg-blue-700" 
                              : "bg-gray-400 cursor-not-allowed"
                            }
                          >
                            {hasExams ? "Assign Vote" : "No Exams"}
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
          setSuccessMessage('Exam created successfully');
          setTimeout(() => setSuccessMessage(null), 3000); // Clear message after 3 seconds
          loadData();
        }}
      />
      
      <AssignVoteToUserModal
        isOpen={showAssignVoteModal}
        onClose={() => {
          setShowAssignVoteModal(false);
          setSelectedUserId(null);
          setSelectedUserEmail('');
        }}
        userId={selectedUserId}
        userEmail={selectedUserEmail}
        onSuccess={() => {
          setShowAssignVoteModal(false);
          setSelectedUserId(null);
          setSelectedUserEmail('');
          setSuccessMessage('Vote assigned successfully');
          setTimeout(() => setSuccessMessage(null), 3000); // Clear message after 3 seconds
          loadData();
        }}
      />
    </div>
  );
}
