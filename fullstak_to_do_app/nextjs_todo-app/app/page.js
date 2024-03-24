'use client'

import { useState, useEffect } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [editTaskId, setEditTaskId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');

  const fetchTasks = async () => {
    const { data } = await api.get('/tasks/');
    setTasks(data);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const addTask = async (e) => {
    e.preventDefault();
    await api.post('/tasks/', { title: newTask, description: newDescription });
    setNewTask('');
    setNewDescription('');
    fetchTasks();
  };

  const updateTask = async () => {
    if (editTaskId !== null) {
      const updatedTask = { title: editTitle, description: editDescription };
      await api.patch(`/tasks/${editTaskId}`, updatedTask);
      setEditTaskId(null); // Reset edit state
      setEditTitle('');
      setEditDescription('');
      fetchTasks();
    }
  };
  

  const deleteTask = async (id) => {
    await api.delete(`/tasks/${id}`);
    fetchTasks();
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 bg-cyan-200">
      <h1 className="text-3xl font-bold text-center mb-8">To Do Task Application</h1>
      <form onSubmit={addTask} className="flex flex-col gap-4 mb-8">
        <input
          className="p-2 border border-gray-300 rounded"
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          placeholder="Task Title"
          required
        />
        <input
          className="p-2 border border-gray-300 rounded"
          value={newDescription}
          onChange={(e) => setNewDescription(e.target.value)}
          placeholder="Task Description"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition-colors">Add Task</button>
      </form>

      <ul className="flex flex-col gap-4">
        {tasks.map((task) => (
          <li key={task.id} className="p-4 border border-gray-200 rounded shadow">
            {editTaskId === task.id ? (
              <div className="flex flex-col gap-2">
                <input
                  className="p-2 border border-gray-300 rounded"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Title"
                />
                <input
                  className="p-2 border border-gray-300 rounded"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Description"
                />
                <div className="flex gap-2">
                  <button onClick={updateTask} className="bg-green-500 text-white p-2 rounded hover:bg-green-600 transition-colors">Update</button>
                  <button onClick={() => setEditTaskId(null)} className="bg-gray-500 text-white p-2 rounded hover:bg-gray-600 transition-colors">Cancel</button>
                </div>
              </div>
            ) : (
              <div className="flex justify-between items-center">
                <span>{task.title}: {task.description || 'No Description'}</span>
                <div className="flex gap-2">
                  <button onClick={() => {
                    setEditTaskId(task.id);
                    setEditTitle(task.title);
                    setEditDescription(task.description);
                  }} className="bg-yellow-500 text-white p-2 rounded hover:bg-yellow-600 transition-colors">Edit</button>
                  <button onClick={() => deleteTask(task.id)} className="bg-red-500 text-white p-2 rounded hover:bg-red-600 transition-colors">Delete</button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );

}
