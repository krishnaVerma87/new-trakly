import React, { useState, useEffect } from 'react'; // Added useEffect
import { useAuth } from '@/contexts/AuthContext';
import { commentsService } from '@/lib/services/comments.service';
import { CommentResponse } from '@/types';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { UserAvatar } from '@/components/ui/UserAvatar';
import toast from 'react-hot-toast';

interface IssueCommentsProps {
    issueId: string;
    projectId: string;
}

export const IssueComments: React.FC<IssueCommentsProps> = ({ issueId }) => {
    const { user } = useAuth();
    const [comments, setComments] = useState<CommentResponse[]>([]);
    const [newComment, setNewComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadComments();
    }, [issueId]);

    const loadComments = async () => {
        try {
            const response = await commentsService.getIssueComments(issueId);
            setComments(response.data);
        } catch (error) {
            console.error('Failed to load comments:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        try {
            setSubmitting(true);
            const response = await commentsService.createComment({
                issue_id: issueId,
                content: newComment,
            });
            setComments((prev) => [...prev, response.data]);
            setNewComment('');
            toast.success('Comment added');
        } catch (error: any) {
            toast.error('Failed to add comment');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="p-4 text-center text-gray-500">Loading comments...</div>;

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Comments ({comments.length})</h3>

            <div className="space-y-6">
                {comments.map((comment) => (
                    <div key={comment.id} className="flex gap-4">
                        <UserAvatar user={comment.user} className="w-10 h-10 mt-1" />
                        <div className="flex-1 space-y-2">
                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-gray-900">{comment.user.full_name}</span>
                                    <span className="text-sm text-gray-500">
                                        {new Date(comment.created_at).toLocaleString()}
                                    </span>
                                </div>
                                <div
                                    className="prose prose-sm max-w-none text-gray-800"
                                    dangerouslySetInnerHTML={{ __html: comment.content }}
                                />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex gap-4">
                {user && <UserAvatar user={user} className="w-10 h-10" />}
                <div className="flex-1">
                    <form onSubmit={handleSubmit}>
                        <RichTextEditor
                            content={newComment}
                            onChange={setNewComment}
                            placeholder="Write a comment..."
                            minHeight="100px"
                        />
                        <div className="mt-2 flex justify-end">
                            <button
                                type="submit"
                                disabled={submitting || !newComment.trim()}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {submitting ? 'Posting...' : 'Post Comment'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
