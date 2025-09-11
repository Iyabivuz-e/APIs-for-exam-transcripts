/**
 * Assign Vote Modal Component
 * 
 * Modal for supervisors to assign votes to ungraded user exams
 */

import React, { useState, useEffect } from 'react';
import { Button, Input, Card } from './ui';
import { apiClient } from '../services/api';

interface UngradedAssignment {
  user_id: number;
  user_email: string;
  exam_id: number;
  exam_title: string;
  exam_date: string;
}

interface AssignVoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AssignVoteModal({ isOpen, onClose, onSuccess }: AssignVoteModalProps) {
  const [assignments, setAssignments] = useState<UngradedAssignment[]>([]);
  const [selectedAssignment, setSelectedAssignment] = useState<UngradedAssignment | null>(null);
  const [vote, setVote] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Load ungraded assignments when modal opens
  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      setIsLoadingData(true);
      setError(null);
      
      const ungradedAssignments = await apiClient.getUngradedAssignments();
      setAssignments(ungradedAssignments || []);
      
    } catch (err) {
      setError('Failed to load ungraded assignments');
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAssignment || !vote) {
      setError('Please select an assignment and enter a vote');
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
      await apiClient.assignVote(selectedAssignment.exam_id, {
        user_id: selectedAssignment.user_id,
        vote: voteNumber
      });

      setSelectedAssignment(null);
      setVote('');
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to assign vote');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedAssignment(null);
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
            <h2 className="text-xl font-bold text-gray-900">Assign Vote</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          {isLoadingData ? (
            <div className="text-center py-4">
              <div className="text-gray-600">Loading ungraded assignments...</div>
            </div>
          ) : assignments.length === 0 ? (
            <div className="text-center py-4">
              <div className="text-gray-600">No ungraded assignments found.</div>
              <p className="text-sm text-gray-500 mt-2">
                All user exams have been graded.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  {error}
                </div>
              )}

              {/* Assignment Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Assignment to Grade
                </label>
                <select
                  value={selectedAssignment ? `${selectedAssignment.user_id}-${selectedAssignment.exam_id}` : ''}
                  onChange={(e) => {
                    if (e.target.value) {
                      const [userId, examId] = e.target.value.split('-').map(Number);
                      const assignment = assignments.find(
                        a => a.user_id === userId && a.exam_id === examId
                      );
                      setSelectedAssignment(assignment || null);
                    } else {
                      setSelectedAssignment(null);
                    }
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Choose an assignment...</option>
                  {assignments.map((assignment) => (
                    <option 
                      key={`${assignment.user_id}-${assignment.exam_id}`}
                      value={`${assignment.user_id}-${assignment.exam_id}`}
                    >
                      {assignment.user_email} - {assignment.exam_title} ({assignment.exam_date})
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

              {/* Selected Assignment Details */}
              {selectedAssignment && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Assignment Details:</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div><strong>Email:</strong> {selectedAssignment.user_email}</div>
                    <div><strong>Exam:</strong> {selectedAssignment.exam_title}</div>
                    <div><strong>Date:</strong> {selectedAssignment.exam_date}</div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={isLoading || !selectedAssignment || !vote}
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