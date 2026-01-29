import type { Task } from '../types';

interface TaskListProps {
  tasks: Task[];
  onComplete: (taskId: number) => void;
  emptyMessage: string;
}

export function TaskList({ tasks, onComplete, emptyMessage }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#d32f2f';
      case 'medium': return '#f57c00';
      case 'low': return '#388e3c';
      default: return '#666';
    }
  };

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className="task-item">
          <div className="task-info">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h4>{task.title}</h4>
              {task.is_recurring && (
                <span style={{ fontSize: '0.9em', color: '#666' }} title="Recurring task">
                  🔄
                </span>
              )}
            </div>
            {task.description && <p>{task.description}</p>}
            <div className="task-meta">
              <span className={`task-badge ${task.task_source === 'auto_generated' ? 'auto' : 'manual'}`}>
                {task.task_source === 'auto_generated' ? 'Auto' : 'Manual'}
              </span>
              <span
                className="task-badge"
                style={{
                  backgroundColor: getPriorityColor(task.priority),
                  color: 'white',
                  marginLeft: '5px'
                }}
              >
                {task.priority}
              </span>
              <span>Due: {task.due_date}</span>
              {' • '}
              <span>Type: {task.task_type}</span>
            </div>
          </div>
          <button
            className="btn"
            onClick={() => onComplete(task.id)}
            style={{ marginLeft: '15px' }}
          >
            Complete
          </button>
        </li>
      ))}
    </ul>
  );
}
