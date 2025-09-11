/**
 * Assign Vote to User Modal Component
 * 
 * Modal for supervisors to assign votes to a specific user's exams
 */

import React, { useState, useEffect } from 'react';
import { Button, Input, Card } from './ui';
import { apiClient } from '../services/api';

interface UserExamAssignment {
  user_id: number;
  user_email: string;
  exam_id: number;
  exam_title: string;
  exam_date: string;
}

interface AssignVoteToUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  userId: number | null;
  userEmail: string;
}

export function AssignVoteToUserModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  userId, 
  userEmail 
}: AssignVoteToUserModalProps) {
  const [userExams, setUserExams] = useState<UserExamAssignment[]>([]);
  const [selectedExam, setSelectedExam] = useState<UserExamAssignment | null>(null);
  const [vote, setVote] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Load user's ungraded exams when modal opens
  useEffect(() => {
    if (isOpen && userId) {
      loadUserExams();
    }
  }, [isOpen, userId]);

  const loadUserExams = async () => {
    try {
      setIsLoadingData(true);
      setError(null);
      
      // Get all ungraded assignments and filter for this user
      const ungradedAssignments = await apiClient.getUngradedAssignments();
      const userAssignments = ungradedAssignments.filter((assignment: any) => 
        assignment.user_id === userId
      );
      
      setUserExams(userAssignments || []);
      console.log(`📚 Loaded ungraded exams for user ${userEmail}:`, userAssignments);
    } catch (err) {
      setError('Failed to load user exams');
      console.error('Error loading user exams:', err);
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedExam || !vote) {
      setError('Please select an exam and enter a vote');
      return;
    }

    const voteNumber = parseFloat(vote);
    if (isNaN(voteNumber) || voteNumber < 0 || voteNumber > 100) {
      setError('Vote must be a number between 0 and 100');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.assignVote(selectedExam.exam_id, {
        user_id: selectedExam.user_id,
        vote: voteNumber
      });

      console.log(`✅ Vote assigned: ${userEmail} - ${selectedExam.exam_title} - ${voteNumber}`);
      setSelectedExam(null);
      setVote('');
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('❌ Vote assignment failed:', err);
      setError(err.message || 'Failed to assign vote');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedExam(null);
    setVote('');
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Assign Vote to {userEmail}
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          {isLoadingData ? (
            <div className="text-center py-4">
              <div className="text-gray-600">Loading user's exams...</div>
            </div>
          ) : userExams.length === 0 ? (
            <div className="text-center py-4">
              <div className="text-gray-600">No ungraded exams found for this user.</div>
              <p className="text-sm text-gray-500 mt-2">
                This user has no exams to grade.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  {error}
                </div>
              )}

              {/* Exam Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Exam to Grade
                </label>
                <select
                  value={selectedExam ? selectedExam.exam_id.toString() : ''}
                  onChange={(e) => {
                    if (e.target.value) {
                      const examId = parseInt(e.target.value);
                      const exam = userExams.find(exam => exam.exam_id === examId);
                      setSelectedExam(exam || null);
                    } else {
                      setSelectedExam(null);
                    }
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Choose an exam...</option>
                  {userExams.map((exam) => (
                    <option key={exam.exam_id} value={exam.exam_id.toString()}>
                      {exam.exam_title} ({new Date(exam.exam_date).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              {/* Vote Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vote (0-100)
                </label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={vote}
                  onChange={(e) => setVote(e.target.value)}
                  placeholder="Enter vote (e.g., 85.5)"
                  required
                />
              </div>

              {/* Selected Exam Details */}
              {selectedExam && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Grading:</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div><strong>Student:</strong> {userEmail}</div>
                    <div><strong>Exam:</strong> {selectedExam.exam_title}</div>
                    <div><strong>Date:</strong> {new Date(selectedExam.exam_date).toLocaleDateString()}</div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={isLoading || !selectedExam || !vote}
                  className="flex-1"
                >
                  {isLoading ? 'Assigning...' : 'Assign Vote'}
                </Button>
                
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleClose}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </div>
      </Card>
    </div>
  );
}
